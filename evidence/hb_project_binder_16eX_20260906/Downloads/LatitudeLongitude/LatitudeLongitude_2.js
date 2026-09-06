//Instantiate the namespace for LatitudeLongitude control
//EDR.CONTROLS = {};
EDR.CONTROLS.LATITUDELONGITUDE = {};

//LatitudeLongitude controls namespace
EDR.CONTROLS.LATITUDELONGITUDE =
{
    ToggleLatitudeLongitudeInput: function (coordType, latValueID, longValueID) {
        //set the value and display/hide the MIN, SEC containers depending on the coordinate type
        var latitudeRootID = this.GetLatitudeLongitudeRootID(latValueID.id);
        var longitudeRoodID = this.GetLatitudeLongitudeRootID(longValueID.id);
        var dvggllPrefix = $("div[id$='DEG']").attr('class').substring(0, $("div[id$='DEG']").attr('class').indexOf('_'));

        //figure out the coordType value
        var coordTypeVal = "";
        if (coordType.value) {
            coordTypeVal = coordType.value;
        }
        else {
            coordTypeVal = coordType.val();
        }

        //initiate the lat long utility object
        switch (coordTypeVal) {
            case "Degrees":
                //no conversion required, value of deg is the same as the hidden values
                var degrees = EDR.LatitudeLongitudeUtilities.ConvertDecimalDegreesToDegrees(latValueID.value);
                degrees = parseInt(degrees * 1000000) / 1000000;

                $('#' + latitudeRootID + 'CNT_DEG_TXT').val(this.ParseValue(degrees));

                degrees = EDR.LatitudeLongitudeUtilities.ConvertDecimalDegreesToDegrees(longValueID.value);
                degrees = parseInt(degrees * 1000000) / 1000000;

                $('#' + longitudeRoodID + 'CNT_DEG_TXT').val(this.ParseValue(degrees));

                // // get reference and change width to container for degrees input
                $("div[id$='DEG']").addClass(dvggllPrefix + '_degreeContainerD');
                $("div[id$='DEG']").removeClass(dvggllPrefix + '_degreeContainerDM');
                $("div[id$='DEG']").removeClass(dvggllPrefix + '_degreeContainerDMS');

                //hide MIN and SEC divs
                var minDiv = $("div[id$='MIN']");
                if (minDiv) {
                    this.HandleHideAnimation(minDiv);
                }
                var secDiv = $("div[id$='SEC']");
                if (secDiv) {
                    this.HandleHideAnimation(secDiv); // "blind", { direction: "horizontal" }, 100
                }

                break;
            case "DegreesMinutes":
                //convert and set latitude values
                var degreesMinutes = EDR.LatitudeLongitudeUtilities.ConvertDecimalDegreesToDegreesMinutes(latValueID.value);
                this.SetValue($('#' + latitudeRootID + 'CNT_DEG_TXT'), this.ParseValue(degreesMinutes.Degrees));
                this.SetValue($('#' + latitudeRootID + 'CNT_MIN_TXT'), this.ParseValue(degreesMinutes.Minutes));

                //convert and set longitude values
                degreesMinutes = EDR.LatitudeLongitudeUtilities.ConvertDecimalDegreesToDegreesMinutes(longValueID.value);
                this.SetValue($('#' + longitudeRoodID + 'CNT_DEG_TXT'), this.ParseValue(degreesMinutes.Degrees));
                this.SetValue($('#' + longitudeRoodID + 'CNT_MIN_TXT'), this.ParseValue(degreesMinutes.Minutes));

                // // get reference and change width to container for degrees input
                $("div[id$='DEG']").removeClass(dvggllPrefix + '_degreeContainerD');
                $("div[id$='DEG']").addClass(dvggllPrefix + '_degreeContainerDM');
                $("div[id$='DEG']").removeClass(dvggllPrefix + '_degreeContainerDMS');
                $("div[id$='MIN']").removeClass(dvggllPrefix + '_minuteContainerD');
                $("div[id$='MIN']").addClass(dvggllPrefix + '_minuteContainerDM');
                $("div[id$='MIN']").removeClass(dvggllPrefix + '_minuteContainerDMS');

                //display the min div and hide the sec div
                var minDiv = $("div[id$='MIN']");
                if (minDiv) {
                    this.HandleShowAnimation(minDiv);
                }
                var secDiv = $("div[id$='SEC']");
                if (secDiv) {
                    this.HandleHideAnimation(secDiv);
                }
                break;
            case "DegreesMinutesSeconds":
                //convert and set latitude values
                var degreesMinutesSeconds = EDR.LatitudeLongitudeUtilities.ConvertDecimalDegreesToDegreesMinutesSeconds(latValueID.value);
                this.SetValue($('#' + latitudeRootID + 'CNT_DEG_TXT'), this.ParseValue(degreesMinutesSeconds.Degrees));
                this.SetValue($('#' + latitudeRootID + 'CNT_MIN_TXT'), this.ParseValue(degreesMinutesSeconds.Minutes));
                this.SetValue($('#' + latitudeRootID + 'CNT_SEC_TXT'), this.ParseValue(degreesMinutesSeconds.Seconds));

                //convert and set longitude values
                degreesMinutesSeconds = EDR.LatitudeLongitudeUtilities.ConvertDecimalDegreesToDegreesMinutesSeconds(longValueID.value);
                this.SetValue($('#' + longitudeRoodID + 'CNT_DEG_TXT'), this.ParseValue(degreesMinutesSeconds.Degrees));
                this.SetValue($('#' + longitudeRoodID + 'CNT_MIN_TXT'), this.ParseValue(degreesMinutesSeconds.Minutes));
                this.SetValue($('#' + longitudeRoodID + 'CNT_SEC_TXT'), this.ParseValue(degreesMinutesSeconds.Seconds));

                // // get reference and change width to container for degrees inputOK

                $("div[id$='DEG']").removeClass(dvggllPrefix + '_degreeContainerD');
                $("div[id$='DEG']").removeClass(dvggllPrefix + '_degreeContainerDM');
                $("div[id$='DEG']").addClass(dvggllPrefix + '_degreeContainerDMS');
                $("div[id$='MIN']").removeClass(dvggllPrefix + '_minuteContainerD');
                $("div[id$='MIN']").removeClass(dvggllPrefix + '_minuteContainerDM');
                $("div[id$='MIN']").addClass(dvggllPrefix + '_minuteContainerDMS');
                $("div[id$='SEC']").removeClass(dvggllPrefix + '_secondContainerD');
                $("div[id$='SEC']").removeClass(dvggllPrefix + '_secondContainerDM');
                $("div[id$='SEC']").addClass(dvggllPrefix + '_secondContainerDMS');

                //display all divs
                var minDiv = $("div[id$='MIN']");
                if (minDiv) {
                    this.HandleShowAnimation(minDiv);
                }
                var secDiv = $("div[id$='SEC']");
                if (secDiv) {
                    this.HandleShowAnimation(secDiv);
                }
                break;
        }
    },

    SetValue: function (source, value) {
        if (source[0].tagName == 'SPAN') {
            source.html(value);
        }
        else {
            source.val(value);
        }
    },

    //returns empty string if value is nothing or 0
    ParseValue: function (val) {
        if ((val == NaN) || (val == 0))
            return "";
        else
            return val;
    },

    HandleHideAnimation: function (source) {
        var visible = source.is(":visible");
        if (visible) {
            source.hide({ direction: 'horizontal' }, 5000);
            //source.animate({ width: '0%' }, 100, () { source.hide(); });
        }
    },

    HandleShowAnimation: function (source) {
        var visible = source.is(":visible");
        if (!visible) {
            source.show({ direction: 'horizontal' }, 5000);
            //source.animate({ width: '100%' }, 5000, () { source.show(); });
        }
    },

    GetLatitudeLongitudeRootID: function (sourceID) {
        var rootID = "";
        if (sourceID) {
            //Since CNT tag is common for all input ids, check for the VAL tag first.				
            if (sourceID.lastIndexOf('VAL') > 0)
                rootID = sourceID.substring(0, sourceID.lastIndexOf('VAL'));
            else if (sourceID.lastIndexOf('CNT_') > 0)
                rootID = sourceID.substring(0, sourceID.lastIndexOf('CNT_'));
        }
        return rootID;
    },

    //Sets the value of the latitude/longitude value based on the coordinate type
    HandleLatitudeLongitudeValueChangeV2: function (source, coordType, isLongitude) {
			var src = document.getElementById(source);
			var cType = document.getElementById(coordType);
			
			EDR.CONTROLS.LATITUDELONGITUDE.HandleLatitudeLongitudeValueChange(src, cType, isLongitude);
    },

    //Sets the value of the latitude/longitude value based on the coordinate type
    HandleLatitudeLongitudeValueChange: function (source, coordType, isLongitude) {
        //first get the degree, minute and second values
        var deg, min, sec;
        var rootID = this.GetLatitudeLongitudeRootID(source.id);
        var decDeg = $('#' + rootID + "VAL"); //hidden decimal degree
        var decVal = NaN;

        if (rootID && decDeg) {
            
            //depending on the coordinate type, convert the degree, minute and second values into degree value
            switch (coordType.value) {
                case "Degrees":
                    deg = $('#' + rootID + "CNT_DEG_TXT").val();
                    decVal = EDR.LatitudeLongitudeUtilities.ConvertDegreesToDecimalDegrees(deg);
                    break;
                case "DegreesMinutes":
                    deg = $('#' + rootID + "CNT_DEG_TXT").val();
                    min = $('#' + rootID + "CNT_MIN_TXT").val();
                    decVal = EDR.LatitudeLongitudeUtilities.ConvertDegreesMinutesToDecimalDegrees(deg, min);
                    break;
                case "DegreesMinutesSeconds":
                    deg = $('#' + rootID + "CNT_DEG_TXT").val();
                    min = $('#' + rootID + "CNT_MIN_TXT").val();
                    sec = $('#' + rootID + "CNT_SEC_TXT").val();
                    decVal = EDR.LatitudeLongitudeUtilities.ConvertDegreesMinutesSecondsToDecimalDegrees(deg, min, sec);
                    break;
            }

            //set the value if its not nothing
            var curVal = EDR.Trim(source.value);

            if (!isNaN(decVal)) {
                if ((isLongitude == true) && (decVal > 0.0)) {
                    decVal = decVal * -1;
                    source.value = deg * -1;
                }
                decDeg.val(decVal);
            }
            else if (curVal != '') {
                alert(curVal + ' is not a valid number.');
                source.value = '';
            }
        }
    },

    //takes a json paramater that contains lat/long hidden ids and returns lat/long values in json
    GetCoordinates: function (latlongID) {
        //parse the hidden ids and get the lat/long values
        var lat = parseFloat(EDR.Trim($('#' + latlongID.LatitudeHiddenID).val()));
        var lng = lng = parseFloat(EDR.Trim($('#' + latlongID.LongitudeHiddenID).val()));
        //create a json object that will return lat/long values
        var latlongValues = { "Latitude": lat, "Longitude": lng };
        return latlongValues;
    },

    //takes a json paramater that contains lat/long hidden ids and values, sets the values
    SetCoordinates: function (latlongValues) {
        //get the lat/long values from the json object and set them to the hidden lat/long fields
        var lat = latlongValues.Latitude;
        var lng = latlongValues.Longitude;
        var latHiddenID = latlongValues.LatitudeHiddenID;
        var longHiddenID = latlongValues.LongitudeHiddenID;
        $('#' + latHiddenID).val(lat);
        $('#' + longHiddenID).val(lng);

        //update the textboxes by calling the ToggleLatitudeLongitudeValue
        //we need to get the current selected coordinate type
        //note: first call to GetLatitudeLongitudeRootID is to strip the 'val' and the second is to strip away the lat
        var rootID = this.GetLatitudeLongitudeRootID(this.GetLatitudeLongitudeRootID(latHiddenID));
        var coordTypeID = rootID + "CNT_COORD_DDL";
        var coordType = $("#" + coordTypeID);

        this.ToggleLatitudeLongitudeInput(coordType, document.getElementById(latHiddenID), document.getElementById(longHiddenID));
    }
};