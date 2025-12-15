# -*- coding: utf-8 -*-
from flask import (Blueprint, request, jsonify, current_app)
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from exts import db
from models import DoctorInfo, DoctorSchedule, CustomerReservation, CustomerInfo
from sqlalchemy import event

# 补充缺失的生成唯一业务编号函数（如果项目中已存在可忽略）
def generate_unique_business_no(prefix, model, field):
    """
    生成唯一的业务编号
    格式：前缀 + 年月日 + 6位自增序号（如：CUS20251215000001）
    """
    today = datetime.now().strftime("%Y%m%d")
    # 查询当天最大的编号
    max_no = db.session.query(func.max(field)).filter(field.like(f"{prefix}{today}%")).scalar()
    if max_no:
        # 提取序号部分并自增
        seq = int(max_no[-6:]) + 1
    else:
        seq = 1
    # 拼接编号
    return f"{prefix}{today}{seq:06d}"

# 为CustomerInfo添加before_insert事件，自动生成customer_no（如果模型中未添加）
@event.listens_for(CustomerInfo, 'before_insert')
def generate_customer_no(mapper, connection, target):
    """插入客户数据前，自动生成客户业务编号"""
    target.customer_no = generate_unique_business_no(
        prefix='CUS',
        model=CustomerInfo,
        field=CustomerInfo.customer_no
    )

bp = Blueprint("doer", __name__, url_prefix="/")

# --------------------------- 数据模型验证类 ---------------------------
class ReservationRequest(BaseModel):
    """预约请求参数模型"""
    customer_phone: str = Field(..., description="客户手机号")
    schedule_id: int = Field(..., description="排班ID")
    project: str = Field(..., description="预约项目")
    appointment_time: str = Field(..., description="预约时间（格式：%Y-%m-%d %H:%M）")

    @validator('customer_phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if not v.isdigit() or len(v) not in [11]:
            raise ValueError('手机号必须是11位数字')
        return v

    @validator('appointment_time')
    def validate_appointment_time(cls, v):
        """验证预约时间格式和有效性"""
        try:
            app_time = datetime.strptime(v, '%Y-%m-%d %H:%M')
            if app_time < datetime.now():
                raise ValueError('预约时间不能早于当前时间')
            return v
        except ValueError:
            raise ValueError('预约时间格式错误，应为：YYYY-MM-DD HH:MM')

    @validator('project')
    def validate_project(cls, v):
        """验证预约项目非空"""
        if not v.strip():
            raise ValueError('预约项目不能为空')
        return v.strip()

class CustomerAddRequest(BaseModel):
    """添加客户请求参数模型"""
    customer_name: str = Field(..., description="客户姓名")
    phone: str = Field(..., description="客户手机号")
    store_id: int = Field(..., description="所属门店ID")
    gender: int = Field(default=2, description="性别（0:女 1:男 2:未知）")
    age: int = Field(None, description="客户年龄")
    email: str = Field(None, description="客户邮箱")
    wechat: str = Field(None, description="客户微信号")
    birthday: str = Field(None, description="客户生日（格式：%Y-%m-%d）")
    address: str = Field(None, description="客户联系地址")
    member_level: int = Field(default=0, description="会员等级（0:普通 1:银卡 2:金卡 3:钻石卡）")
    source: str = Field(None, description="客户来源")
    emergency_contact: str = Field(None, description="紧急联系人")
    emergency_phone: str = Field(None, description="紧急联系人电话")
    allergy_history: str = Field(None, description="过敏史")
    medical_history: str = Field(None, description="既往病史")
    doctor_id: int = Field(None, description="专属医生ID")

    @validator('customer_name')
    def validate_name(cls, v):
        """验证姓名非空"""
        if not v.strip():
            raise ValueError('客户姓名不能为空')
        return v.strip()

    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if not v.isdigit() or len(v) != 11:
            raise ValueError('手机号必须是11位数字')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        """验证性别值"""
        if v not in [0, 1, 2]:
            raise ValueError('性别值只能是0（女）、1（男）、2（未知）')
        return v

    @validator('member_level')
    def validate_member_level(cls, v):
        """验证会员等级"""
        if v not in [0, 1, 2, 3]:
            raise ValueError('会员等级只能是0（普通）、1（银卡）、2（金卡）、3（钻石卡）')
        return v

    @validator('birthday')
    def validate_birthday(cls, v):
        """验证生日格式"""
        if v is None:
            return v
        try:
            birth_date = datetime.strptime(v, '%Y-%m-%d').date()
            if birth_date > date.today():
                raise ValueError('生日不能晚于当前日期')
            return v
        except ValueError:
            raise ValueError('生日格式错误，应为：YYYY-MM-DD')

    @validator('emergency_phone')
    def validate_emergency_phone(cls, v):
        """验证紧急联系人电话"""
        if v is None:
            return v
        if not v.isdigit():
            raise ValueError('紧急联系人电话必须是数字')
        return v

# --------------------------- 通用响应函数 ---------------------------
def api_response(code=200, msg="success", data=None):
    return jsonify({
        "code": code,  # 200成功/400参数错误/404不存在/500服务器错误
        "msg": msg,
        "data": data or {}
    }), code

# --------------------------- 新增客户接口 ---------------------------
@bp.route('/api/add/customers', methods=['POST'])
def add_customer():
    """
    添加客户（客户注册）
    请求方式：POST
    请求体：JSON
    返回：新增客户信息
    """
    try:
        # 1. 获取请求数据
        req_data = request.get_json() or {}
        if not req_data:
            return api_response(400, "请求体不能为空")

        # 2. 参数验证
        try:
            customer_req = CustomerAddRequest(**req_data)
        except ValueError as e:
            return api_response(400, f"参数验证失败：{str(e)}")

        # 3. 业务逻辑校验
        # 检查手机号是否已存在
        existing_customer = CustomerInfo.query.filter_by(phone=customer_req.phone).first()
        if existing_customer:
            return api_response(400, "该手机号已注册，请勿重复添加")

        # 检查专属医生是否存在（如果传了doctor_id）
        if customer_req.doctor_id:
            doctor = DoctorInfo.query.get(customer_req.doctor_id)
            if not doctor:
                return api_response(404, "指定的专属医生不存在")

        # 4. 构建客户对象
        birthday = None
        if customer_req.birthday:
            birthday = datetime.strptime(customer_req.birthday, '%Y-%m-%d').date()

        customer = CustomerInfo(
            customer_name=customer_req.customer_name,
            gender=customer_req.gender,
            age=customer_req.age,
            phone=customer_req.phone,
            email=customer_req.email,
            wechat=customer_req.wechat,
            birthday=birthday,
            address=customer_req.address,
            member_level=customer_req.member_level,
            source=customer_req.source,
            doctor_id=customer_req.doctor_id,
            store_id=customer_req.store_id,
            emergency_contact=customer_req.emergency_contact,
            emergency_phone=customer_req.emergency_phone,
            allergy_history=customer_req.allergy_history,
            medical_history=customer_req.medical_history
        )

        # 5. 保存到数据库
        db.session.add(customer)
        db.session.commit()

        # 6. 返回结果
        return api_response(
            data={
                "customer_id": customer.id,
                "customer_no": customer.customer_no,
                "customer_name": customer.customer_name,
                "phone": customer.phone,
                "store_id": customer.store_id
            }
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"添加客户失败：数据库错误 - {str(e)}")
        return api_response(500, "服务器内部错误（数据库异常）")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加客户失败：{str(e)}")
        return api_response(500, f"添加客户失败：{str(e)}")

# --------------------------- 客户预约接口（优化版） ---------------------------
@bp.route('/api/customer/reservation', methods=['POST'])
def customer_reservation():
    """
    客户预约接口
    请求方式：POST
    请求体：JSON
    参数：
        customer_phone: 客户手机号
        schedule_id: 排班ID
        project: 预约项目
        appointment_time: 预约时间（格式：%Y-%m-%d %H:%M）
    """
    try:
        # 1. 获取请求数据
        req_data = request.get_json() or {}
        if not req_data:
            return api_response(400, "请求体不能为空")

        # 2. 参数验证
        try:
            reservation_req = ReservationRequest(**req_data)
        except ValueError as e:
            return api_response(400, f"参数验证失败：{str(e)}")

        # 3. 业务逻辑校验
        # 3.1 查询客户
        customer = CustomerInfo.query.filter_by(phone=reservation_req.customer_phone).first()
        if not customer:
            return api_response(404, "客户不存在，请先注册")

        # 检查客户状态
        if customer.customer_status != 1:
            return api_response(403, f"客户状态异常（{customer.customer_status}），无法预约")

        # 3.2 查询排班（加行锁防止并发）
        schedule = db.session.query(DoctorSchedule).with_for_update().filter_by(
            id=reservation_req.schedule_id
        ).first()
        if not schedule:
            return api_response(404, "排班信息不存在")

        # 检查排班状态
        if schedule.schedule_status == 0:
            return api_response(403, "该排班时段已暂停，无法预约")
        if schedule.schedule_status == 2:
            return api_response(403, "该排班时段已约满，无法预约")

        # 3.3 检查预约项目是否在排班限制内
        if schedule.project_limit and reservation_req.project not in schedule.project_limit:
            return api_response(403, f"该排班时段仅支持预约：{','.join(schedule.project_limit)}")

        # 3.4 检查医生状态
        doctor = DoctorInfo.query.get(schedule.doctor_id)
        if not doctor or doctor.status != 1:
            return api_response(403, "医生状态异常，无法预约")

        # 3.5 检查是否重复预约
        existing_reservation = CustomerReservation.query.filter(
            and_(
                CustomerReservation.customer_id == customer.id,
                CustomerReservation.schedule_id == schedule.id,
                CustomerReservation.reservation_status.in_([1, 2])  # 正确：使用in_()实现IN查询
            )
        ).first()
        if existing_reservation:
            return api_response(403, "你已预约该时段，请勿重复预约")

        # 4. 构建预约记录
        appointment_time = datetime.strptime(reservation_req.appointment_time, '%Y-%m-%d %H:%M')
        reservation = CustomerReservation(
            customer_id=customer.id,
            schedule_id=schedule.id,
            project=reservation_req.project,
            appointment_time=appointment_time,
            reservation_status=1  # 待确认
        )

        # 5. 更新排班人数和状态
        schedule.current_reserve += 1
        if schedule.current_reserve >= schedule.max_reserve:
            schedule.schedule_status = 2

        # 6. 提交事务
        db.session.add(reservation)
        db.session.add(schedule)
        db.session.commit()

        # 7. 返回结果
        return api_response(
            msg="预约成功",
            data={
                "reservation_no": reservation.reservation_no,
                "customer_name": customer.customer_name,
                "doctor_name": doctor.doctor_name,
                "schedule_date": schedule.schedule_date.strftime('%Y-%m-%d'),
                "start_time": schedule.start_time.strftime('%H:%M'),
                "project": reservation.project,
                "appointment_time": reservation.appointment_time.strftime('%Y-%m-%d %H:%M'),
                "status": reservation.reservation_status
            }
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"预约失败：数据库错误 - {str(e)}")
        return api_response(500, "服务器内部错误（数据库异常）")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"预约失败：{str(e)}")
        return api_response(500, f"预约失败：{str(e)}")

# --------------------------- 取消预约接口（优化版） ---------------------------
@bp.route('/api/customer/reservation/cancel', methods=['POST'])
def cancel_reservation():
    """
    取消预约接口
    请求参数：reservation_no（预约编号）、cancel_reason（取消原因）
    """
    try:
        req_data = request.get_json() or {}
        reservation_no = req_data.get('reservation_no')
        cancel_reason = req_data.get('cancel_reason', '')

        if not reservation_no:
            return api_response(400, "预约编号不能为空")

        # 查询预约记录并加锁
        reservation = db.session.query(CustomerReservation).with_for_update().filter_by(
            reservation_no=reservation_no
        ).first()
        if not reservation:
            return api_response(404, "预约记录不存在")

        # 检查预约状态
        if reservation.reservation_status in [0, 3, 4]:
            return api_response(403, "该预约已取消/完成/爽约，无法重复操作")

        # 更新预约状态
        reservation.reservation_status = 0
        reservation.cancel_reason = cancel_reason

        # 更新排班信息
        schedule = reservation.schedule
        schedule.current_reserve = max(0, schedule.current_reserve - 1)
        if schedule.current_reserve < schedule.max_reserve:
            schedule.schedule_status = 1

        # 提交事务
        db.session.add(reservation)
        db.session.add(schedule)
        db.session.commit()

        return api_response(
            msg="取消预约成功",
            data={"reservation_no": reservation_no}
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"取消预约失败：{str(e)}")
        return api_response(500, "服务器内部错误（数据库异常）")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"取消预约失败：{str(e)}")
        return api_response(500, f"取消预约失败：{str(e)}")

# --------------------------- 原有接口（保持不变） ---------------------------
@bp.route('/api/add/doctors', methods=['POST'])
def add_doctor():
    try:
        req_data = request.get_json() or {}
        required_fields = ['doctor_name', 'qualification', 'store_id']
        for field in required_fields:
            if not req_data.get(field):
                return api_response(400, f"参数缺失：{field}")

        doctor = DoctorInfo(
            doctor_name=req_data['doctor_name'],
            gender=req_data.get('gender', 0),
            age=req_data.get('age'),
            title=req_data.get('title'),
            specialty=req_data.get('specialty'),
            qualification=req_data['qualification'],
            work_years=req_data.get('work_years'),
            introduction=req_data.get('introduction'),
            avatar=req_data.get('avatar'),
            store_id=req_data['store_id'],
            internal_contact=req_data.get('internal_contact'),
            status=req_data.get('status', 1)
        )

        db.session.add(doctor)
        db.session.commit()

        return api_response(data={
            "doctor_id": doctor.id,
            "doctor_no": doctor.doctor_no,
            "doctor_name": doctor.doctor_name
        })
    except KeyError as e:
        db.session.rollback()
        return api_response(400, f"参数错误：缺少{e}字段")
    except Exception as e:
        db.session.rollback()
        return api_response(500, f"新增医生失败：{str(e)}")

@bp.route('/api/get/doctors', methods=['GET'])
def get_doctor_list():
    try:
        store_id = request.args.get('store_id')
        status = request.args.get('status')
        specialty = request.args.get('specialty')

        query = DoctorInfo.query
        if store_id:
            query = query.filter_by(store_id=store_id)
        if status:
            query = query.filter_by(status=status)
        if specialty:
            query = query.filter(DoctorInfo.specialty.contains(specialty))

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        paginate = query.paginate(page=page, per_page=per_page)

        doctor_list = []
        for doc in paginate.items:
            doctor_list.append({
                "doctor_id": doc.id,
                "doctor_no": doc.doctor_no,
                "doctor_name": doc.doctor_name,
                "gender": doc.gender,
                "title": doc.title,
                "specialty": doc.specialty,
                "work_years": doc.work_years,
                "status": doc.status,
                "store_id": doc.store_id
            })

        return api_response(data={
            "list": doctor_list,
            "total": paginate.total,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        return api_response(500, f"查询医生列表失败：{str(e)}")

@bp.route('/api/put/doctors/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    try:
        doctor = DoctorInfo.query.get(doctor_id)
        if not doctor:
            return api_response(404, "医生不存在")

        req_data = request.get_json() or {}

        if 'doctor_name' in req_data:
            doctor.doctor_name = req_data['doctor_name']
        if 'gender' in req_data:
            doctor.gender = req_data['gender']
        if 'title' in req_data:
            doctor.title = req_data['title']
        if 'specialty' in req_data:
            doctor.specialty = req_data['specialty']
        if 'work_years' in req_data:
            doctor.work_years = req_data['work_years']
        if 'introduction' in req_data:
            doctor.introduction = req_data['introduction']
        if 'avatar' in req_data:
            doctor.avatar = req_data['avatar']
        if 'internal_contact' in req_data:
            doctor.internal_contact = req_data['internal_contact']
        if 'status' in req_data:
            doctor.status = req_data['status']
        if 'age' in req_data:
            doctor.age = req_data['age']

        db.session.commit()
        return api_response(msg="更新医生信息成功")
    except Exception as e:
        db.session.rollback()
        return api_response(500, f"更新医生信息失败：{str(e)}")

@bp.route('/api/doctors/<int:doctor_id>/status', methods=['PATCH'])
def change_doctor_status(doctor_id):
    try:
        doctor = DoctorInfo.query.get(doctor_id)
        if not doctor:
            return api_response(404, "医生不存在")

        req_data = request.get_json() or {}
        new_status = req_data.get('status')
        if new_status not in [0, 1, 2, 3]:
            return api_response(400, "状态值错误（0:离职 1:在职 2:休假 3:暂停接诊）")

        doctor.status = new_status
        db.session.commit()
        return api_response(msg=f"医生状态已调整为：{new_status}")
    except Exception as e:
        db.session.rollback()
        return api_response(500, f"调整医生状态失败：{str(e)}")

@bp.route('/api/add/schedules', methods=['POST'])
def add_schedule():
    try:
        req_data = request.get_json() or {}
        required_fields = ['doctor_id', 'store_id', 'schedule_date', 'start_time', 'end_time']
        for field in required_fields:
            if not req_data.get(field):
                return api_response(400, f"参数缺失：{field}")

        doctor = DoctorInfo.query.filter_by(id=req_data['doctor_id'], status=1).first()
        if not doctor:
            return api_response(400, "医生不存在或已离职/暂停接诊")

        try:
            schedule_date = datetime.strptime(req_data['schedule_date'], "%Y-%m-%d").date()
            start_time = datetime.strptime(req_data['start_time'], "%H:%M:%S").time()
            end_time = datetime.strptime(req_data['end_time'], "%H:%M:%S").time()
        except:
            return api_response(400, "日期/时间格式错误（日期：2025-12-15，时间：09:00:00）")

        if end_time <= start_time:
            return api_response(400, "结束时间必须晚于开始时间")

        schedule = DoctorSchedule(
            doctor_id=req_data['doctor_id'],
            store_id=req_data['store_id'],
            schedule_date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            max_reserve=req_data.get('max_reserve', 5),
            current_reserve=req_data.get('current_reserve', 0),
            project_limit=req_data.get('project_limit'),
            schedule_status=req_data.get('schedule_status', 1),
            remark=req_data.get('remark')
        )

        db.session.add(schedule)
        db.session.commit()

        return api_response(data={
            "schedule_id": schedule.id,
            "schedule_no": schedule.schedule_no,
            "doctor_name": doctor.doctor_name
        })
    except Exception as e:
        db.session.rollback()
        return api_response(500, f"新增排班失败：{str(e)}")

@bp.route('/api/get/schedules', methods=['GET'])
def get_schedule_list():
    try:
        doctor_id = request.args.get('doctor_id')
        store_id = request.args.get('store_id')
        schedule_date = request.args.get('schedule_date')
        schedule_status = request.args.get('schedule_status')

        query = DoctorSchedule.query
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if store_id:
            query = query.filter_by(store_id=store_id)
        if schedule_date:
            try:
                date_obj = datetime.strptime(schedule_date, "%Y-%m-%d").date()
                query = query.filter_by(schedule_date=date_obj)
            except:
                return api_response(400, "日期格式错误（2025-12-15）")
        if schedule_status:
            query = query.filter_by(schedule_status=schedule_status)

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        paginate = query.paginate(page=page, per_page=per_page)

        schedule_list = []
        for sch in paginate.items:
            schedule_list.append({
                "schedule_id": sch.id,
                "schedule_no": sch.schedule_no,
                "doctor_id": sch.doctor_id,
                "doctor_name": sch.doctor.doctor_name,
                "store_id": sch.store_id,
                "schedule_date": sch.schedule_date.strftime("%Y-%m-%d"),
                "start_time": sch.start_time.strftime("%H:%M:%S"),
                "end_time": sch.end_time.strftime("%H:%M:%S"),
                "max_reserve": sch.max_reserve,
                "current_reserve": sch.current_reserve,
                "schedule_status": sch.schedule_status,
                "project_limit": sch.project_limit,
                "remark": sch.remark
            })

        return api_response(data={
            "list": schedule_list,
            "total": paginate.total,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        return api_response(500, f"查询排班失败：{str(e)}")

@bp.route('/api/put/schedules/<int:schedule_id>/reserve', methods=['PATCH'])
def update_reserve_count(schedule_id):
    try:
        schedule = DoctorSchedule.query.get(schedule_id)
        if not schedule:
            return api_response(404, "排班记录不存在")

        req_data = request.get_json() or {}
        operate_type = req_data.get('type')
        if operate_type not in [1, 2]:
            return api_response(400, "操作类型错误（1:新增预约 2:取消预约）")

        if operate_type == 1:
            if schedule.current_reserve >= schedule.max_reserve:
                return api_response(400, "该时段已约满")
            schedule.current_reserve += 1
            if schedule.current_reserve == schedule.max_reserve:
                schedule.schedule_status = 2
        else:
            if schedule.current_reserve <= 0:
                return api_response(400, "已预约人数不能小于0")
            schedule.current_reserve -= 1
            if schedule.schedule_status == 2 and schedule.current_reserve < schedule.max_reserve:
                schedule.schedule_status = 1

        db.session.commit()
        return api_response(data={
            "current_reserve": schedule.current_reserve,
            "schedule_status": schedule.schedule_status
        })
    except Exception as e:
        db.session.rollback()
        return api_response(500, f"调整预约人数失败：{str(e)}")

@bp.route('/api/del/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        schedule = DoctorSchedule.query.get(schedule_id)
        if not schedule:
            return api_response(404, "排班记录不存在")

        if schedule.current_reserve > 0:
            return api_response(400, "该时段已有预约，禁止删除")

        db.session.delete(schedule)
        db.session.commit()
        return api_response(msg="删除排班成功")
    except Exception as e:
        db.session.rollback()
        return api_response(500, f"删除排班失败：{str(e)}")

@bp.route('/api/doctors/available', methods=['GET','POST'])
def get_available_doctors():
    try:
        if request.method == 'GET':
            specialty = request.args.get('specialty')
            schedule_date = request.args.get('schedule_date')
            store_id = request.args.get('store_id')
        else:
            req_data = request.get_json() or {}
            specialty = req_data.get('specialty')
            schedule_date = req_data.get('schedule_date')
            store_id = req_data.get('store_id')

        if not specialty:
            return api_response(400, "参数缺失：擅长项目（specialty）")
        if not schedule_date:
            return api_response(400, "参数缺失：预约日期（schedule_date，格式：2025-12-15）")

        try:
            target_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
        except ValueError:
            return api_response(400, "日期格式错误，正确格式：2025-12-15")

        doctor_query = DoctorInfo.query.filter(
            func.json_contains(DoctorInfo.specialty, func.json_quote(specialty)),
            DoctorInfo.status == 1
        )
        if store_id:
            doctor_query = doctor_query.filter_by(store_id=store_id)
        eligible_doctors = doctor_query.all()

        if not eligible_doctors:
            return api_response(200, "暂无擅长该项目的在职医生", data=[])

        doctor_status_list = []
        available_list = []
        for doctor in eligible_doctors:
            all_schedules = doctor.schedules.filter(
                DoctorSchedule.schedule_date == target_date
            ).order_by(DoctorSchedule.start_time).all()

            if not all_schedules:
                doctor_status_list.append({
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.doctor_name,
                    "status_type": "no_schedule",
                    "status_msg": f"医生{doctor.doctor_name}在{target_date}暂无排班",
                    "available_time_slots": []
                })
                continue

            valid_schedules = [
                s for s in all_schedules
                if s.schedule_status == 1 and s.current_reserve < s.max_reserve
            ]

            if valid_schedules:
                time_slots = []
                for schedule in valid_schedules:
                    time_slots.append({
                        "schedule_id": schedule.id,
                        "schedule_no": schedule.schedule_no,
                        "start_time": schedule.start_time.strftime("%H:%M:%S"),
                        "end_time": schedule.end_time.strftime("%H:%M:%S"),
                        "remaining": schedule.max_reserve - schedule.current_reserve,
                        "project_limit": schedule.project_limit
                    })

                available_list.append({
                    "doctor_id": doctor.id,
                    "doctor_no": doctor.doctor_no,
                    "doctor_name": doctor.doctor_name,
                    "title": doctor.title,
                    "specialty": doctor.specialty,
                    "store_id": doctor.store_id,
                    "available_time_slots": time_slots
                })

                doctor_status_list.append({
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.doctor_name,
                    "status_type": "空闲",
                    "status_msg": f"{doctor.doctor_name}在{target_date}有可用预约时段",
                    "available_time_slots": time_slots
                })
            else:
                full_schedules = [s for s in all_schedules if s.current_reserve >= s.max_reserve]
                pause_schedules = [s for s in all_schedules if s.schedule_status == 0]

                if full_schedules and pause_schedules:
                    status_msg = f"医生{doctor.doctor_name}在{target_date}的排班部分暂停且部分已约满"
                elif full_schedules:
                    status_msg = f"医生{doctor.doctor_name}在{target_date}的排班已全部约满"
                else:
                    status_msg = f"医生{doctor.doctor_name}在{target_date}的排班已全部暂停"

                doctor_status_list.append({
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.doctor_name,
                    "status_type": "unavailable",
                    "status_msg": status_msg,
                    "available_time_slots": []
                })

        return api_response(
            code=200,
            msg="查询成功" if available_list else "暂无可用医生及时段",
            data={
                "available_doctors": available_list,
                "doctor_status_detail": doctor_status_list
            }
        )
    except Exception as e:
        return api_response(500, f"查询可预约医生失败：{str(e)}")


# --------------------------- 预约查询请求参数验证（可选，用于复杂参数校验） ---------------------------
class ReservationQueryRequest(BaseModel):
    """预约查询参数模型（用于接口文档和参数校验，GET请求可按需使用）"""
    customer_phone: str = Field(None, description="客户手机号")
    reservation_no: str = Field(None, description="预约编号")
    schedule_id: int = Field(None, description="排班ID")
    reservation_status: int = Field(None, description="预约状态（0:取消 1:待确认 2:已确认 3:已完成 4:爽约）")
    start_time: str = Field(None, description="预约开始时间（格式：%Y-%m-%d %H:%M）")
    end_time: str = Field(None, description="预约结束时间（格式：%Y-%m-%d %H:%M）")
    page: int = Field(1, description="页码")
    per_page: int = Field(10, description="每页条数")

    @validator('customer_phone')
    def validate_phone(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError('手机号必须是11位数字')
        return v

    @validator('reservation_status')
    def validate_status(cls, v):
        if v and v not in [0, 1, 2, 3, 4]:
            raise ValueError('预约状态值错误（0:取消 1:待确认 2:已确认 3:已完成 4:爽约）')
        return v

    @validator('start_time', 'end_time')
    def validate_time(cls, v):
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d %H:%M')
            except ValueError:
                raise ValueError('时间格式错误，应为：YYYY-MM-DD HH:MM')
        return v

# --------------------------- 查询预约接口 ---------------------------
@bp.route('/api/customer/reservation/query', methods=['GET'])
def query_reservation():
    """
    查询客户预约记录
    请求方式：GET
    查询参数：
        customer_phone: 客户手机号（可选）
        reservation_no: 预约编号（可选）
        schedule_id: 排班ID（可选）
        reservation_status: 预约状态（0:取消 1:待确认 2:已确认 3:已完成 4:爽约）（可选）
        start_time: 预约开始时间（格式：%Y-%m-%d %H:%M）（可选）
        end_time: 预约结束时间（格式：%Y-%m-%d %H:%M）（可选）
        page: 页码（默认1）
        per_page: 每页条数（默认10）
    返回：分页的预约记录列表
    """
    try:
        # 1. 获取查询参数
        customer_phone = request.args.get('customer_phone')
        reservation_no = request.args.get('reservation_no')
        schedule_id = request.args.get('schedule_id')
        reservation_status = request.args.get('reservation_status')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # 2. 参数预处理和校验
        # 转换状态为整数
        if reservation_status:
            try:
                reservation_status = int(reservation_status)
                if reservation_status not in [0, 1, 2, 3, 4]:
                    return api_response(400, "预约状态值错误（0:取消 1:待确认 2:已确认 3:已完成 4:爽约）")
            except ValueError:
                return api_response(400, "预约状态必须为数字")

        # 转换排班ID为整数
        if schedule_id:
            try:
                schedule_id = int(schedule_id)
            except ValueError:
                return api_response(400, "排班ID必须为数字")

        # 转换时间为datetime对象
        start_time_obj = None
        if start_time:
            try:
                start_time_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            except ValueError:
                return api_response(400, "开始时间格式错误，应为：YYYY-MM-DD HH:MM")

        end_time_obj = None
        if end_time:
            try:
                end_time_obj = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
            except ValueError:
                return api_response(400, "结束时间格式错误，应为：YYYY-MM-DD HH:MM")

        # 3. 构建查询条件
        query = CustomerReservation.query

        # 关联查询（客户、排班、医生），提升查询效率
        query = query.join(CustomerInfo, CustomerReservation.customer_id == CustomerInfo.id)
        query = query.join(DoctorSchedule, CustomerReservation.schedule_id == DoctorSchedule.id)
        query = query.join(DoctorInfo, DoctorSchedule.doctor_id == DoctorInfo.id)

        # 按条件过滤
        if customer_phone:
            query = query.filter(CustomerInfo.phone == customer_phone)
        if reservation_no:
            query = query.filter(CustomerReservation.reservation_no == reservation_no)
        if schedule_id:
            query = query.filter(CustomerReservation.schedule_id == schedule_id)
        if reservation_status is not None:
            query = query.filter(CustomerReservation.reservation_status == reservation_status)
        if start_time_obj:
            query = query.filter(CustomerReservation.appointment_time >= start_time_obj)
        if end_time_obj:
            query = query.filter(CustomerReservation.appointment_time <= end_time_obj)

        # 按创建时间倒序排序
        query = query.order_by(CustomerReservation.create_time.desc())

        # 4. 分页处理
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)

        # 5. 格式化返回数据
        reservation_list = []
        for res in paginate.items:
            # 构建状态描述
            status_desc = {
                0: "取消",
                1: "待确认",
                2: "已确认",
                3: "已完成",
                4: "爽约"
            }.get(res.reservation_status, "未知")

            reservation_list.append({
                "reservation_id": res.id,
                "reservation_no": res.reservation_no,
                "customer_id": res.customer_id,
                "customer_name": res.customer.customer_name,
                "customer_phone": res.customer.phone,
                "doctor_id": res.schedule.doctor_id,
                "doctor_name": res.schedule.doctor.doctor_name,
                "schedule_id": res.schedule_id,
                "schedule_date": res.schedule.schedule_date.strftime('%Y-%m-%d'),
                "schedule_start_time": res.schedule.start_time.strftime('%H:%M'),
                "schedule_end_time": res.schedule.end_time.strftime('%H:%M'),
                "project": res.project,
                "reservation_status": res.reservation_status,
                "reservation_status_desc": status_desc,
                "appointment_time": res.appointment_time.strftime('%Y-%m-%d %H:%M'),
                "cancel_reason": res.cancel_reason,
                "create_time": res.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                "update_time": res.update_time.strftime('%Y-%m-%d %H:%M:%S')
            })

        # 6. 返回结果
        return api_response(
            data={
                "list": reservation_list,
                "total": paginate.total,
                "page": page,
                "per_page": per_page,
                "pages": paginate.pages
            }
        )

    except SQLAlchemyError as e:
        current_app.logger.error(f"查询预约记录失败：数据库错误 - {str(e)}")
        return api_response(500, "服务器内部错误（数据库异常）")
    except Exception as e:
        current_app.logger.error(f"查询预约记录失败：{str(e)}")
        return api_response(500, f"查询预约记录失败：{str(e)}")


# --------------------------- 查询客户请求参数验证 ---------------------------
class CustomerQueryRequest(BaseModel):
    """客户查询参数模型"""
    customer_phone: str = Field(None, description="客户手机号")
    customer_name: str = Field(None, description="客户姓名（支持模糊查询）")
    member_level: int = Field(None, description="会员等级（0:普通 1:银卡 2:金卡 3:钻石卡）")
    store_id: int = Field(None, description="所属门店ID")
    customer_status: int = Field(None, description="客户状态（0:冻结 1:正常 2:拉黑 3:注销）")
    doctor_id: int = Field(None, description="专属医生ID")
    page: int = Field(1, description="页码")
    per_page: int = Field(10, description="每页条数")

    @validator('customer_phone')
    def validate_phone(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError('手机号必须是11位数字')
        return v

    @validator('member_level')
    def validate_member_level(cls, v):
        if v and v not in [0, 1, 2, 3]:
            raise ValueError('会员等级只能是0（普通）、1（银卡）、2（金卡）、3（钻石卡）')
        return v

    @validator('customer_status')
    def validate_customer_status(cls, v):
        if v and v not in [0, 1, 2, 3]:
            raise ValueError('客户状态只能是0（冻结）、1（正常）、2（拉黑）、3（注销）')
        return v

    @validator('store_id', 'doctor_id')
    def validate_int_params(cls, v):
        if v and not isinstance(v, int):
            raise ValueError('该参数必须为整数')
        return v

# --------------------------- 查询客户接口 ---------------------------
@bp.route('/api/get/customers', methods=['GET'])
def get_customer_list():
    """
    查询客户列表
    请求方式：GET
    查询参数：
        customer_phone: 客户手机号（可选，精确匹配）
        customer_name: 客户姓名（可选，模糊匹配）
        member_level: 会员等级（0:普通 1:银卡 2:金卡 3:钻石卡）（可选）
        store_id: 所属门店ID（可选）
        customer_status: 客户状态（0:冻结 1:正常 2:拉黑 3:注销）（可选）
        doctor_id: 专属医生ID（可选）
        page: 页码（默认1）
        per_page: 每页条数（默认10）
    返回：分页的客户列表及统计信息
    """
    try:
        # 1. 获取查询参数
        customer_phone = request.args.get('customer_phone')
        customer_name = request.args.get('customer_name')
        member_level = request.args.get('member_level')
        store_id = request.args.get('store_id')
        customer_status = request.args.get('customer_status')
        doctor_id = request.args.get('doctor_id')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # 2. 参数预处理与校验
        # 转换数字类型参数
        params = {
            'member_level': member_level,
            'store_id': store_id,
            'customer_status': customer_status,
            'doctor_id': doctor_id
        }
        for key, value in params.items():
            if value:
                try:
                    params[key] = int(value)
                except ValueError:
                    return api_response(400, f"{key}必须为整数")

        # 校验手机号格式
        if customer_phone and (not customer_phone.isdigit() or len(customer_phone) != 11):
            return api_response(400, "手机号必须是11位数字")

        # 校验会员等级
        if params['member_level'] and params['member_level'] not in [0, 1, 2, 3]:
            return api_response(400, "会员等级只能是0（普通）、1（银卡）、2（金卡）、3（钻石卡）")

        # 校验客户状态
        if params['customer_status'] and params['customer_status'] not in [0, 1, 2, 3]:
            return api_response(400, "客户状态只能是0（冻结）、1（正常）、2（拉黑）、3（注销）")

        # 3. 构建查询条件
        query = CustomerInfo.query

        # 关联医生表，获取专属医生姓名（左连接，避免无专属医生的客户被过滤）
        query = query.outerjoin(DoctorInfo, CustomerInfo.doctor_id == DoctorInfo.id)

        # 精确条件过滤
        if customer_phone:
            query = query.filter(CustomerInfo.phone == customer_phone)
        if params['member_level'] is not None:
            query = query.filter(CustomerInfo.member_level == params['member_level'])
        if params['store_id']:
            query = query.filter(CustomerInfo.store_id == params['store_id'])
        if params['customer_status'] is not None:
            query = query.filter(CustomerInfo.customer_status == params['customer_status'])
        if params['doctor_id']:
            query = query.filter(CustomerInfo.doctor_id == params['doctor_id'])

        # 模糊查询客户姓名
        if customer_name:
            query = query.filter(CustomerInfo.customer_name.like(f"%{customer_name}%"))

        # 按创建时间倒序排序
        query = query.order_by(CustomerInfo.create_time.desc())

        # 4. 分页处理
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)

        # 5. 格式化返回数据（转换数字状态为中文描述）
        gender_desc = {0: "女", 1: "男", 2: "未知"}
        member_level_desc = {0: "普通会员", 1: "银卡会员", 2: "金卡会员", 3: "钻石会员"}
        customer_status_desc = {0: "冻结", 1: "正常", 2: "拉黑", 3: "注销"}

        customer_list = []
        for customer in paginate.items:
            customer_list.append({
                "customer_id": customer.id,
                "customer_no": customer.customer_no,
                "customer_name": customer.customer_name,
                "gender": customer.gender,
                "gender_desc": gender_desc.get(customer.gender, "未知"),
                "age": customer.age,
                "phone": customer.phone,
                "email": customer.email,
                "wechat": customer.wechat,
                "birthday": customer.birthday.strftime("%Y-%m-%d") if customer.birthday else None,
                "address": customer.address,
                "member_level": customer.member_level,
                "member_level_desc": member_level_desc.get(customer.member_level, "普通会员"),
                "member_points": customer.member_points,
                "source": customer.source,
                "doctor_id": customer.doctor_id,
                "doctor_name": customer.doctor.doctor_name if customer.doctor else None,
                "store_id": customer.store_id,
                "emergency_contact": customer.emergency_contact,
                "emergency_phone": customer.emergency_phone,
                "allergy_history": customer.allergy_history,
                "medical_history": customer.medical_history,
                "customer_status": customer.customer_status,
                "customer_status_desc": customer_status_desc.get(customer.customer_status, "正常"),
                "remark": customer.remark,
                "create_time": customer.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "update_time": customer.update_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        # 6. 返回结果
        return api_response(
            data={
                "list": customer_list,
                "total": paginate.total,
                "page": page,
                "per_page": per_page,
                "pages": paginate.pages
            }
        )

    except SQLAlchemyError as e:
        current_app.logger.error(f"查询客户列表失败：数据库错误 - {str(e)}")
        return api_response(500, "服务器内部错误（数据库异常）")
    except Exception as e:
        current_app.logger.error(f"查询客户列表失败：{str(e)}")
        return api_response(500, f"查询客户列表失败：{str(e)}")