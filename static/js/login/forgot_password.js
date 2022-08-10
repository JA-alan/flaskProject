function bindCaptchaBtnClick(){
    $("#captcha-btn").on("click",function (event){
        var $this = $(this);
        var email = $("input[name='email']").val();

        if (!email){
            alert("请先输入邮箱");
            return;
        }
        //通过js请求接口：ajax
        //$.get("user")
        $.ajax({
            url: "/user/send/password/verification",
            method:"POST",
            data:{
                "email":email
            },
            success: function (res){
                var code = res["code"];
                if(code === 200){
                    //限制重复点击
                    $this.off("click");
                    var countDown = 60;
                    var timer = setInterval(function (){
                        countDown -= 1;
                        if(countDown > 0){
                        $this.text(countDown+"秒后重新发送");
                        }else{
                            $this.text("获取验证码");
                            //重新绑定点击事件
                            bindCaptchaBtnClick();
                            //清除倒计时，否则死循环
                            clearInterval(timer);
                        }

                    },1000)
                    alert("验证码发送成功");
                }else {
                    alert(res["msg"]);
                }
            }
        })
    });
}



//网页渲染完再执行
$(function () {
    bindCaptchaBtnClick();
});



// var toastTrigger = document.getElementById('liveToastBtn')
// var toastLiveExample = document.getElementById('liveToast')
// if (toastTrigger) {
//   toastTrigger.addEventListener('click', function () {
//     var toast = new bootstrap.Toast(toastLiveExample)
//
//     toast.show()
//   })
// }