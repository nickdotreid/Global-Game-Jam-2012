$(document).ready(function(){
	$(".map").bind("initialize",function(){
		map_container = $(this);
		var myOptions = {
			center: new google.maps.LatLng(	37.78392669999999, -122.3924249),
			zoom: 15,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};
		var map = new google.maps.Map(this,myOptions);
		map_container.data("map",map);
		
		google.maps.event.addListener(map, 'click', function(event) {
			if(map_container.hasClass("target")){
				map_container.trigger({
					type:"add_marker",
					lat:event.latLng.lat(),
					lng:event.latLng.lng()
				});				
			}
		});
					
	}).bind("add_marker",function(event){
		map = $(this).data("map");
		if(!map){
			return false;
		}
		if($(this).data("marker")){
			$(this).data("marker").setMap(null);
		}
		marker = new google.maps.Marker({
			position: new google.maps.LatLng(event.lat, event.lng),
			map: map
		});
		if(event.lat && event.lng){
			$("form input.target[name=lat]").val(event.lat);
			$("form input.target[name=lng]").val(event.lng);
		}
		$(this).data("marker",marker);
	}).bind("add_player",function(event){
		map = $(this).data("map");
		if(!map){
			return false;
		}
		if($(this).data("person")){
			$(this).data("person").setMap(null);
		}
		var circle_options = {
	      strokeColor: "#0000FF",
	      strokeOpacity: 0.8,
	      strokeWeight: 2,
	      fillColor: "#0000FF",
	      fillOpacity: 0.35,
	      map: map,
	      center: new google.maps.LatLng(event.lat, event.lng),
	      radius: 40
	    };
	    circle = new google.maps.Circle(circle_options);
		$(this).data("person",circle);
	}).bind("set_center",function(event){
		map = $(this).data("map");
		if(!map){
			return true;
		}
		map.setCenter(new google.maps.LatLng(event.lat, event.lng))
	});
	$(".map").trigger("initialize");
});