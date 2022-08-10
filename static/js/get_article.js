function getArticleWeb(){
    // js发送http请求 利用相应的代码片段-->
    var xhr = new XMLHttpRequest(); // 初始化js中的内置对象XMLHttpRequest-->
    //定义 事件绑定中的函数，定义在xhr实例化之后，因为函数中需要xhr
    function success() {
    //console.log("完成请求-响应啦！！！！！！！") //请求响应成功后再打印
    //console.log(xhr.responseText) //拿到 响应的响应体信息,响应正文
    console.log(xhr.status)       //拿到请求的响应状态码
}

    xhr.onload = success;//当请求响应完成后，去执行success函数

    xhr.open("get", "/auth/user/article");// 提供HTTP请求的 方法和url-->

    xhr.send();// 发起真正的请求-->

    console.log("ajax请求已发送")//先打印
}

$(function () {
    getArticleWeb();
});