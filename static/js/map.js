$(document).ready(function(){
	$(".map").bind("initialize",function(){
		map_container = $(this);
		var myOptions = {
			center: new google.maps.LatLng(-34.397, 150.644),
			zoom: 13,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};
		var map = new google.maps.Map(this,myOptions);
		map_container.data("map",map);
		
		google.maps.event.addListener(map, 'click', function(event) {
			if(map_container.data("marker")){
				map_container.data("marker").setMap(null);
			}
			marker = new google.maps.Marker({
				position: event.latLng,
				map: map
			});
			map_container.data("marker",marker).trigger({
				type:"setCenter",
				lat:event.latLng.lat(),
				lng:event.latLng.lng()
			});
		});
					
	}).bind("setCenter",function(event){
		map = $(this).data("map");
		if(!map){
			return true;
		}
		if(event.lat && event.lng){
			map.setCenter(new google.maps.LatLng(event.lat, event.lng))
			$("form input[name=lat]").val(event.lat);
			$("form input[name=lng]").val(event.lng);
		}
	});
	$(".map").trigger("initialize");
});