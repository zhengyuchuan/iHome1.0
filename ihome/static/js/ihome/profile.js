function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $("#form-avatar").submit(function (e) {
        e.preventDefault();
        // 利用插件提供的ajaxSubmit提交图片数据
        $(this).ajaxSubmit({
            url:"/api/v1/users/avatar",
            type:"post",
            dataType:"json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success:function (resp) {
                if(resp.errno=="0"){
                    // 上传成功
                    var avatar_url = resp.data.avatar_url;
                    $("#user-avatar").attr("src", avatar_url);
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    });


    $("#form-name").submit(function (e) {
        e.preventDefault();
        var user_name = $("#user-name").val();
        if(!user_name){
            $(".error-msg" ).text("用户名不能为空");
            $(".error-msg").show();
            return
        }
        var data = {
            user_name:user_name
        };
        var data_json = JSON.stringify(data);
        $.ajax({
            url:"/api/v1/users/name",
            data:data_json,
            contentType:"application/json",
            type:"post",
            dataType:"json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success:function (resp) {
                if(resp.errno=="0"){
                    // 上传成功
                    location.href="/"
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    });
});

