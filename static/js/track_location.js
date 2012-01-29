$(document).ready(function(){
	if(navigator.geolocation){
		navigator.geolocation.getCurrentPosition(function(position){
			$.ajax({
				url:"/track",
				type:"POST",
				dataType:"JSON",
				data:{
					lat:position.coords.latitude,
					lng:position.coords.longitude
				},
				success:function(data){
					if(data['success']){
						$(".map").trigger({
							type:"set_center",
							lat:position.coords.latitude,
							lng:position.coords.longitude
						});
						$("input.user.coords[name=lat]").val(position.coords.latitude);
						$("input.user.coords[name=lng]").val(position.coords.longitude);
					}
				}
			})
		});
	}
});