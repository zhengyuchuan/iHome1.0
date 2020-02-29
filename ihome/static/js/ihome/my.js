function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url:"/api/v1/session",
        type:"delete",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        dataType:"json",
        success:function (resp) {
            if(resp.errno=="0"){
                location.href = "/index.html"
            }
        }
    })
}

$(document).ready(function(){
});