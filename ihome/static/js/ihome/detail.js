function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    // 获取url中房源编号，并传递给后端
    var query_data = decodeQuery();
    var house_id = query_data["id"];

    $.get("/api/v1/houses/" + house_id, function (resp) {
        if(resp.errno==="0"){
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:resp.data.house.img_urls, price:resp.data.price}));
            $(".detail-con").html(template("house-detail-tmpl", {house:resp.data.house}));
            // 如果两个id不相等，那么就不是房主本人，则展示预定按钮
            if (resp.data.user_id!==resp.data.house.user_id){
                $(".book-house").attr("href", "/booking.html?hid=" + resp.data.house.hid);
                $(".book-house").show();
                    var mySwiper = new Swiper ('.swiper-container', {
                        loop: true,
                        autoplay: 2000,
                        autoplayDisableOnInteraction: false,
                        pagination: '.swiper-pagination',
                        paginationType: 'fraction'
                    });
            }
        }
    });
});