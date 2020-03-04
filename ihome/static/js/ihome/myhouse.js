function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function(){
    // $.ajax({
    //     url:"/api/v1/users/auth",
    //     dataType:"json",
    //     type:"get",
    //     headers:{
    //             "X-CSRFToken":getCookie("csrf_token")
    //         },
    //     success:function (resp) {
    //         if(resp.errno==="0"){
    //             // 隐藏实名认证信息
    //             $(".auth-warn").hide();
    //         }else{
    //             $(".auth-warn").show();
    //         }
    //     }
    // });

    $.get("/api/v1/users/auth", function (resp) {
        if(resp.errno==="4101"){
            // 用户未登录
            location.href = "/login.html"
        }else if(resp.errno==="0"){
            // 如果真实姓名与身份证号不完整
            if (!(resp.data.real_name&&resp.data.id_card)){
                $(".auth-warn").show();
                return
            }
            $.get("/api/v1/user/houses", function (resp) {
                if (resp.errno==="0"){
                    $("#houses-list").html(template("houses-list-tmpl", {houses:resp.data.houses}))
                }else {
                    $("#houses-list").html(template("houses-list-tmpl", {houses: []}))
                }
            })
        }
    })

});