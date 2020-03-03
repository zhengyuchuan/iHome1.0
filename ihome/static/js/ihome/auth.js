function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function () {
    $.get("/api/v1/users/auth", function (resp) {
        if (resp.errno=="4101"){
            location.href = "/login.html"
        }else if(resp.errno=="0"){
            if(resp.data.real_name && resp.data.id_card){
                $("#real-name").val(resp.data.real_name)
                $("#id-card").val(resp.data.id_card);
                // 给input添加disabled标签，禁止修改
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                // 隐藏保存按钮
                $("#form-auth>input[type=submit]").hide()
            }
        }else {
            alert(resp.errmsg)
        }
    }, "json")

    // 管理实名信息表单的提交
    $("#form-auth").submit(function (e) {
        e.preventDefault();
        var real_name = $("#real-name").val();
        var id_card = $("#id-card").val();
        if (real_name==='' || id_card==='' ){
            $(".error-msg").show()
        }

        // 将表单的数据转换为json字符串
        var data={
            real_name:real_name,
            id_card:id_card
        };
        var json_data = JSON.stringify(data);
        $.ajax({
            url:"/api/v1/users/auth",
            type:"post",
            data:json_data,
            contentType:"application/json",
            dataType:"json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success:function (resp) {
                if (resp.errno==="0"){
                    $(".error-msg").hide();
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide()
                }
            }
        })
    })
});

