/****************************************************************************************************/
/* JS Namespace library for latitude longitude utilities																																*/
/* Must pre-link these JS files:																																		*/
/*		/global/jscripts/edrlibrary.js																																	*/
/****************************************************************************************************/
EDR.LatitudeLongitudeUtilities = {};

EDR.LatitudeLongitudeUtilities =
{
	//Converts the value to int
	ConvertToInt: function(val) {
		var newVal = parseInt(val, 10); //Specifying radix since 08 and 09 would parse as 0 otherwise
		if (isNaN(newVal)) {
			newVal = 0;
		}
		return newVal;
	},
	
	//converts the value to float
	ConvertToFloat: function(val) {
		var newVal = parseFloat(val);
		if (isNaN(newVal)) {
			newVal = 0;
		}
		return newVal;
	},
	
	//Uses regular expression to check if the value is a number or not
	IsNumber: function (val) {
		var valid = false;
		if (val == null) {
			valid = false;
		}
		else if (val == ""){
			//blank value is also going to be set as valid
			valid = true;
		}
		else {
			var regex = new RegExp('-?[0-9]+(\.[0-9][0-9]?)?');
			if (val.match(regex))
				valid = true;
		}
		return valid;
	},

	//Checks whether longitude value is valid
	IsValidLongitudeValue: function (val) {
		var valid = false;
		if ((val >= -180) && (val <= 90))
			valid = true;
		return valid;
	},

	//Checks whether latitude value is valid
	IsValidLatitudeValue: function (val) {
		var valid = false;
		if ((val >= -90) && (val <= 90))
			valid = true;
		return valid;
	},

	//Checks whether the minute/second value is withing range
	IsValidTimeValue: function (val) {
		var valid = false;
		if ((val >= 0) && (val <= 60))
			valid = true;
		return valid;
	},

	//Validates the degrees value
	//Returns NaN if the value is not a valid number
	ConvertDegreesToDecimalDegrees: function (deg) {
		if (!this.IsNumber(deg)) {
			//alert("Degrees value is not a valid number");
			return NaN;
		}
		else {
			return deg;
		}
	},

	//Converts the degrees minutes to decimal degrees
	//Returns NaN if the value is not a valid number
	//Returns 0 if the value is not a valid minute value
	ConvertDegreesMinutesToDecimalDegrees: function (deg, min) {
		var val = 0;
		//make sure value is valid
		if (!this.IsNumber(deg)) {
			//alert("Degrees value is not a valid number");
			return NaN;
		}

		if (!this.IsNumber(min)) {
			//alert("Minutes value is not a valid number");
			return NaN; //return nothing
		}
		else {
			if (!this.IsValidTimeValue(min))
				return 0;
		}

		//now that the values have been validated, parse them
		var intDeg = this.ConvertToInt(deg);
		var floatMin = this.ConvertToFloat(min);

		//convert the value
		if (intDeg < 0)
			val = intDeg - (floatMin / 60);
		else
			val = intDeg + (floatMin / 60);

		return val;
	},

	//Converts the degrees, minutes and seconds to decimal degrees
	//Returns NaN if the value is not a valid number
	//Returns 0 if the value is not a valid minute value
	ConvertDegreesMinutesSecondsToDecimalDegrees: function (deg, min, sec) {
		var val = 0;
		//make sure value is valid
		if (!this.IsNumber(deg)) {
			//alert("Degrees value is not a valid number");
			return NaN;
		}

		if (!this.IsNumber(min)) {
			//alert("Minutes value is not a valid number");
			return NaN;
		}
		else {
			if (!this.IsValidTimeValue(min))
				return 0;
		}

		if (!this.IsNumber(sec)) {
			//alert("Seconds value is not a valid number");
			return NaN;
		}
		else {
			if (!this.IsValidTimeValue(sec))
				return 0;
		}

		//now that the values have been validated, parse them
		var intDeg = this.ConvertToInt(deg);
		var intMin = this.ConvertToInt(min);
		var floatSec = this.ConvertToFloat(sec);

		//convert the value
		if (intDeg < 0)
			val = intDeg - (intMin / 60) - (floatSec / 3600); // 60 mins = 3600 seconds
		else
			val = intDeg + (intMin / 60) + (floatSec / 3600); // 60 mins = 3600 seconds

		return val;
	},

	//converts the decimal degrees to degrees
	ConvertDecimalDegreesToDegrees: function (val) {
		if (this.IsNumber(val)) {
			return val;
		}
		else {
			return 0;
		}
	},

	//converts the decimal degrees to degrees and minutes
	//returns JSON object
	//	return values: Degrees, Minutes
	ConvertDecimalDegreesToDegreesMinutes: function (val) {
		var iSign;
		var deg, min;

		//find sign
		if (this.IsNumber(val)) {
			if ((val == 0) || (Math.abs(val) == val))
				iSign = 1;
			else {
				iSign = -1;
				val = Math.abs(val);
			}

			//parse the values
			deg = Math.floor(val);
			min = (val - deg) * 60;

			//increment the degrees by 1 if minutes value = 60
			if (deg == 60) {
				deg += 1;
				min = 0;
			}

			//fix sign
			deg *= iSign;
		}
		else {
			//alert("Please enter a valid number!");
			deg = 0;
			min = 0;
		}

		var degreesMinutes = { "Degrees": deg, "Minutes": min.toFixed(4) };
		return degreesMinutes;
	},

	//converts the decimal degrees to degrees, minutes and seconds
	//returns JSON object
	//	return values: Degrees, Minutes, Seconds
	ConvertDecimalDegreesToDegreesMinutesSeconds: function (val) {
		var iSign;
		var deg, min, sec;

		//find sign
		if (this.IsNumber(val)) {
			if ((val == 0) || (Math.abs(val) == val))
				iSign = 1;
			else {
				iSign = -1;
				val = Math.abs(val);
			}

			//parse the values
			deg = Math.floor(val);
			var fMinutes = (val - deg) * 60;
			min = Math.floor(fMinutes);
			sec = (fMinutes - min) * 60;

			//increment the minutes by 1 if seconds value = 60
			if (sec == 60) {
				min += 1;
				sec = 0;
			}

			//increment the degrees by 1 if minutes value = 60
			if (min == 60) {
				deg += 1;
				min = 0;
			}

			//fix sign
			deg *= iSign;
		}
		else {
			//alert("Please enter a valid number!");
			deg = 0;
			min = 0;
			sec = 0;
		}

		var degreesMinutesSeconds = { "Degrees": deg, "Minutes": min, "Seconds": sec.toFixed(2) };
		return degreesMinutesSeconds;
	}
};