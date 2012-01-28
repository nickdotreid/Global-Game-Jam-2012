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
						alert("WIN");
					}
				}
			})
		});
	}
});