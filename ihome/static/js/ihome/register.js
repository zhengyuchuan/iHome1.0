function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    // js中三目运算符
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 形成图片验证码链接地址，设置到页面中
    // 1.生成图片验证码
    imageCodeId = generateUUID();
    var url = "/api/v1/image_codes/" + imageCodeId;
    $(".image-code img").attr("src", url)
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    // 向后端请求的参数
    var req_data = {
        image_code:imageCode, // 图片验证码的值
        image_code_id:imageCodeId //
    };
    $.get("/api/v1/sms_codes/" + mobile, req_data, function (resp) {
        if(resp.errno == '0'){
            var num = 60;
            var timer = setInterval(function () {
                if (num>1){
                    // 修改倒计时文本
                    $(".phonecode-a").html(num+"秒");
                    num -= 1
                } else {
                    $(".phonecode-a").html("获取验证码");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    clearInterval(timer)
                }
            }, 1000, 60)
        }else {
            alert(resp.errmsg );
            $(".phonecode-a").attr("onclick", "sendSMSCode();");
        }
    });
    // $.get("/api/v1/sms_codes/" + mobile, req_data,
    //     function(data){
    //         if (0 != data.errno) {
    //             $("#image-code-err span").html(data.errmsg);
    //             $("#image-code-err").show();
    //             if (2 == data.errno || 3 == data.errno) {
    //                 generateImageCode();
    //             }
    //             $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //         }
    //         else {
    //             var $time = $(".phonecode-a");
    //             var duration = 60;
    //             var intervalid = setInterval(function(){
    //                 $time.html(duration + "秒");
    //                 if(duration === 1){
    //                     clearInterval(intervalid);
    //                     $time.html('获取验证码');
    //                     $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //                 }
    //                 duration = duration - 1;
    //             }, 1000, 60);
    //         }
    // }, 'json');
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    // 拦截表单的提交行为，并将form格式数据替换为json格式
    $(".form-register").submit(function(e){
        // 阻止浏览器对表单的默认提交行为
        e.preventDefault();
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
        }
        // 调用ajax，向后端发送数据
        var req_data = {
            mobile:mobile,
            sms_code:phoneCode,
            password:passwd,
            password2:passwd2
        };
        var req_json = JSON.stringify(req_data);
        $.ajax({
            url:"/api/v1/users",
            type:"post",
            data:req_json,
            contentType:"application/json",
            dataType:"json",
            // CSRFProtect机制可以从表单中提取token，也可以从请求头中提取
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success:function (resp) {
                if(resp.errno == "0"){
                    // 注册成功，跳转至主页
                    location.href = "/index.html"
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    });
});