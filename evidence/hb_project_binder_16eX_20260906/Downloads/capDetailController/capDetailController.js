var capDetailController = {
	showMap: function () {
		var recordIds = $('map[name="map"]').data('record-ids');

		window.GIS.onLocateRecords(recordIds, null, null, function () {
		}, function () {
			console.log('Error Locating Record: ');
			console.log(recordIds);
		});
	}
};
window.GIS.controller = capDetailController;