function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // 向后端获取城区信息
    $.get("/api/v1/areas", function (resp) {
        if (resp.errno==="0"){
            var areas = resp.data;
            var html = template("area-tmpl", {areas:areas})
            $("#area-id").html(html)
        }else {
            alert(resp.errmsg)
        }
    });

    // 发布 新房源信息
    $("#form-house-info").submit(function (e) {
        e.preventDefault();
        var data={};
        // 使用map函数提取表单数据
        $("#form-house-info").serializeArray().map(function (x) {
            data[x.name]=x.value
        });
        // 收集设施id信息
        var facility={};
        $(":checked[name=facility]").each(function (index, x) {
            facility[index]=$(x).val()
        });
        data.facility=facility;

        // 向后端发送请求
        $.ajax({
            url:"/api/v1/houses/info",
            type:"post",
            contentType:"application/json",
            data:JSON.stringify(data),
            dataType:"json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success:function (resp) {
                if(resp.errno==="4101"){
                    location.href="/login.html"
                }else if(resp.errno==="0"){
                    // 隐藏基本信息表单,显示上传图片
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(resp.data.house_id)
                }else{
                    alert(resp.errmsg)
                }
            }
        })

    });


    // 保存房源图片
    $("#form-house-image").submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url:"/api/v1/houses/image",
            type:"post",
            dataType: "json",
            headers: {"X-CSRFToken":getCookie("csrf_token")},
            success:function (resp) {
                if (resp.errno==="4101"){
                    location.href="/login.html"
                }else if(resp.errno==="0"){
                    $(".house-image-cons").append('<img src="' + resp.data.image_url + '" alt="">')
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })


});