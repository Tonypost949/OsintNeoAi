/// <reference path="http://localhost/global/jscripts/edrlibrary.js" />

EDR.POLYFROMFILE = {};
EDR.POLYFROMFILE =
{
    // lastUploadedPolygons is the array which contains the parsed information about all the features in the geometry file uploaded by the user
    lastUploadedPolygons: null,
    // currentFeatureIndex references the lastUploadedPolygons index which is selected
    currentFeatureIndex: -1,
    acceptFeature: function () {
        ///<summary> handles acceptance of the current feature, which saves the polygon </summary>
        /// <returns> </returns>
        try {
            //Clear any previous errors
            EDR.WEBGEOCODER.clearErrorMessages();
            $('#uploadControl1').hide();
            EDR.WEBGEOCODER.plotSelectedPolygon(EDR.POLYFROMFILE.lastUploadedPolygons[EDR.POLYFROMFILE.currentFeatureIndex].coordinates, true, true);
            EDR.POLYFROMFILE.drewPreviewPolygon = false; // clear this flag for the next upload
        } catch (e) {
            if (document.getElementById('lblKmlErrorMessage').innerHTML === '') {
                EDR.WEBGEOCODER.displayKMLErrorMessage("We were unable to access a polygon from the file you uploaded. Please check the polygon information in the file and upload again.  If the error persists, contact us.");
            }
            EDR.WEBGEOCODER.logError('plotSelectedGeoCodedPolygon(): ' + e.message);
        }
    },
    // previewMapMetrics Is a bounding box which encomposes all the features shown in the preview map and the scaling factors to display it on the canvas
    previewMapMetrics: {},
    getPreviewMapMetrics: function (canvas, boundingBox) {
        var mapWidth = boundingBox.maxmax[0] - boundingBox.minmin[0];
        var mapHeight = boundingBox.maxmax[1] - boundingBox.minmin[1];
        var scale = 1;
        if (mapWidth != 0 && mapHeight != 0)
            scale = canvas.width / canvas.height > mapWidth / mapHeight ? canvas.height / mapHeight : canvas.width / mapWidth;
        scale *= 0.90;
        var shiftX = -boundingBox.midmid[0] * scale + 0.5 * canvas.width;
        var shiftY = -boundingBox.midmid[1] * scale + 0.5 * canvas.height;
        return {
            scale,
            shiftX,
            shiftY
        }
    },
    hitTestPreviewMap: function (polys, canvasX, canvasY, metrics) {
        ///<summary> Given a x and y relative to a canvas, and the scaling metrics for the canvas, determins which feature is in that location </summary>
        /// <returns> The index of first feature which is at that location, or -1 if none is found. </returns>
        var tpLatLng = { x: (canvasX - metrics.shiftX) / metrics.scale, y: (canvasY - metrics.shiftY) / metrics.scale };

        for (var polyIndex = 0; polyIndex < polys.length; polyIndex++) {
            if (polys[polyIndex].valid) {
                var overheadLineSegmentCount = polys[polyIndex].worldCoordsSortedLinesegments
                    .filter(sortedTwoPtArray => sortedTwoPtArray[0].x <= tpLatLng.x && sortedTwoPtArray[1].x > tpLatLng.x)
                    .filter(sortedTwoPtArray => {
                        var dy = sortedTwoPtArray[1].y - sortedTwoPtArray[0].y;
                        var dx = sortedTwoPtArray[1].x - sortedTwoPtArray[0].x;
                        var yIntercept = sortedTwoPtArray[0].y + (dy / dx) * (tpLatLng.x - sortedTwoPtArray[0].x);
                        return yIntercept > tpLatLng.y;
                    }).length;

                if (overheadLineSegmentCount % 2 == 1) // if there is a odd number of line segments in the ray pointing up from the pt then it's inside the polygon
                    return polyIndex;
            }
        }
        return -1; // no match
    },
    drawPreviewPolysOnCanvas: function (polys, canvas, metrics, selectedIndex, highlightIndex) {
        ///<summary> Renders polygons on the provided canvas using the scales defined in the metrics paramter. </summary>

        var neutralColor = '#EEEEEE';
        var lineColorSelected = '#3B75A4';
        var fillColorSelected = '#9DBAD888';
        var lineColor = '#686868';
        var fillColor = '#B8B8B888';
        var fillColorInvalid = '#FF000088';
        var lineColorInvalid = '#FF4444';

        var ctx = canvas.getContext('2d');

        // clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // fill the background
        ctx.fillStyle = neutralColor;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // invalid shapes are drawn differently. The user still sees these shapes in the card to help
        // explain why these are not available to select.
        var drawPolyInvalid = function (polyIndex, poly) {
            // draw linesegments connecting the verticies
            for (var p1 = 1; p1 < poly.worldCoords.length; p1++) {
                ctx.beginPath();
                var p0 = p1 - 1;
                ctx.moveTo(metrics.scale * poly.worldCoords[p0].x + metrics.shiftX, metrics.scale * poly.worldCoords[p0].y + metrics.shiftY);
                ctx.lineTo(metrics.scale * poly.worldCoords[p1].x + metrics.shiftX, metrics.scale * poly.worldCoords[p1].y + metrics.shiftY);
                ctx.closePath();
                ctx.lineWidth = 3;
                ctx.strokeStyle = lineColorInvalid;
                ctx.stroke();
            }

            // draw the verticies
            ctx.beginPath();
            poly.worldCoords.forEach((wcp, index) => {
                ctx.beginPath();
                ctx.arc(metrics.scale * wcp.x + metrics.shiftX, metrics.scale * wcp.y + metrics.shiftY, 3, 0, 2 * Math.PI, false);
                ctx.fillStyle = fillColorInvalid;
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = lineColorInvalid;
                ctx.stroke();
            });
        }

        var drawPolyValid = function (polyIndex, poly) {
            ctx.beginPath();
            poly.worldCoords.forEach((wcp, index) => {
                index == 0 ? ctx.moveTo : ctx.lineTo(metrics.scale * wcp.x + metrics.shiftX, metrics.scale * wcp.y + metrics.shiftY);
            });
            ctx.closePath();
            ctx.lineWidth = 3;
            ctx.strokeStyle = (polyIndex == selectedIndex || polyIndex == highlightIndex) ? lineColorSelected : lineColor;
            ctx.stroke();
            ctx.fillStyle = polyIndex == selectedIndex ? fillColorSelected : fillColor;
            ctx.fill();
        }

        var drawPoly = function (polyIndex) {
            if (typeof polyIndex !== 'undefined' && polyIndex >= 0 && polyIndex < polys.length) {
                poly = polys[polyIndex];
                // render function is determined by the valid flag of the polygon
                (poly.valid ? drawPolyValid : drawPolyInvalid)(polyIndex, poly);
            }
        }

        // draw the polygons - note the selected and highlighted polys are drawn last to ensure their borders are not overlapped
        for (var i = 0; i < polys.length; i++) {
            if (i != selectedIndex && i != highlightIndex) {
                drawPoly(i);
            }
        }
        drawPoly(selectedIndex);
        drawPoly(highlightIndex);

    },
    handleCancel: function () {
        if (EDR.POLYFROMFILE.drewPreviewPolygon) {
            // remove the polygon
            EDR.WEBGEOCODER.removePolygon();
            EDR.WEBGEOCODER.tpParcel = null;
            EDR.POLYFROMFILE.drewPreviewPolygon = false;
        }
    },
    drewPreviewPolygon: false,
    drawSelectedCanvasPreview: function (redrawGrid, scrollToSelectedRow, previousSelectedRow) {
        ///<summary> Updates the UI for the uploaded geometry file and selected polygon </summary>

        var htmlEntities = function (str) {
            return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        };

        // many kml file contain a property called 'description' which is HTML
        // since it may contain useful information to describe the features it is parsed
        function parseHTMLDescriptionCellParser(row) {
            var cellBreakdown = row.split(">");
            if (cellBreakdown.length >= 2) {
                var cell = cellBreakdown[1];
                var closeTDPos = cell.indexOf("</td");
                if (closeTDPos > 0) {
                    cell = cell.substring(0, closeTDPos);
                    return cell;
                }
            }
            return undefined;
        }

        function parseHTMLDescriptionProperty(propValue) {
            var result = [];
            if (typeof propValue === 'string') {
                var breakDown = propValue.split("<tr").map(rowBreakDown => rowBreakDown.split("<td"));
                breakDown.filter(row => row.length == 3).map(row => {
                    // row[0] will contain the remainder of the <tr tag and is not useful
                    var rowName = parseHTMLDescriptionCellParser(row[1]);
                    var rowValue = parseHTMLDescriptionCellParser(row[2]);
                    if (typeof rowName !== 'undefined' && typeof rowValue !== 'undefined')
                        result.push({ key: rowName, value: rowValue, parent: 'description' });
                });
            } else {
                console.error(`Description value does not have child value ${JSON.stringify(propValue)}`);
            }
            return result;
        }

        // The feature properties are stored as an object in the geojson. The geojson object has arbitrary attribtutes for each
        // value provided. This function converts that to an array of objects, each with a key attribute, which is the name of the source,
        // and a string value attribute, which is the a parsed value from the source.
        // In the case of the description, the HTML is parsed and broken up into multiple key/values.
        var PropertiesToArrayOfKeyValueObjects = function (props) {
            var result = [];

            Object.keys(props).forEach(key => {
                switch (typeof props[key]) {
                    case 'object':
                        if (Array.isArray(props[key])) {
                            console.error(`Property value is array: ${key} ${JSON.stringify(props[key])}`);

                            result.push({ key, value: htmlEntities(JSON.stringify(props[key])) });
                        } else {
                            if (key == "description" && props[key]["@type"] == "html") {
                                parseHTMLDescriptionProperty(props[key].value).forEach(descriptionProp => {
                                    result.push(descriptionProp);
                                });
                            } else {
                                console.error(`Property value is object: ${key} ${JSON.stringify(props[key])}`);
                                result.push({ key, value: htmlEntities(JSON.stringify(props[key])) });
                            }
                        }
                        break;
                    case 'boolean':
                    case 'number':
                    case 'string':
                        result.push({ key, value: htmlEntities(props[key]) });
                        break;
                    default:
                        console.error(`Unhandled case for property value ${key} ${JSON.stringify(props[key])}`);
                }
            });
            return result;
        };

        var propertySort = function(keyValue1, keyValue2) {
            const nameValueMatches = [/([a-zA-Z].*[0-9])|([0-9].*[a-zA-Z])/, /[a-zA-Z]{3}/];
            for (var i = 0; i < nameValueMatches.length; i++)
                if (nameValueMatches[i].test(keyValue1.value)) {
                    if (!nameValueMatches[i].test(keyValue2.value))
                        return -1;
                } else if (nameValueMatches[i].test(keyValue2.value))
                    return 1;
            if (keyValue1.key < keyValue2.key)
                return -1;
            else if (keyValue1.key > keyValue2.key)
                return 1;
            return 0;
        };

        // propertyFilter is used to determine if a text property that has been parsed from the geometry file will be shown next to a feature
        var propertyFilter = function (key, value) {
            if (typeof (value) != 'string' && typeof (value) != 'number') {
                return false;
            }
            if (value.toString().trim().length == 0) {
                return false;
            }
            var excludePatterns = [/^stroke-/, /^stroke$/, /^fill-/, /^fill$/, /^styleUrl$/, /^label-/];
            for (var i = 0; i < excludePatterns.length; i++) {
                if (excludePatterns[i].test(key)) {
                    return false;
                }
            }

            var includePatterns = [/^name$/i, /^Lat$/i, /^Long$/i, /^site$/i, /^address$/i, /^parcel_id$/i, /^SITE_ADD1$/i, /^LocAddr$/i,
                    /^LocName$/i, /^LATITUDE$/i, /^LONGITUDE$/i, /^SITE LABEL$/i,  /^Site_name$/i, /^siteadd$/i, /^APN$/i];
            return includePatterns.findIndex(pat => pat.test(key)) >= 0;
        };


        var availablePolys = EDR.POLYFROMFILE.lastUploadedPolygons.filter(poly => poly.valid);
        var selectedIndex = EDR.POLYFROMFILE.currentFeatureIndex;
        var canvas = document.getElementById('allPolygonPreviewCanvas');
        if (availablePolys.length > 1) {
            $("#allPolygonPreviewCanvas").show();
            EDR.POLYFROMFILE.drawPreviewPolysOnCanvas(EDR.POLYFROMFILE.lastUploadedPolygons.filter(poly => poly.valid), canvas, EDR.POLYFROMFILE.previewMapMetrics, selectedIndex);
        } else {
            $("#allPolygonPreviewCanvas").hide();
        }

        // select the polygon for now in the main map (the users previous polygon must be cleared to bring up the file upload dialog)
        try {
            if (selectedIndex >= 0) {
                EDR.POLYFROMFILE.drewPreviewPolygon = true;
                EDR.WEBGEOCODER.plotSelectedPolygon(EDR.POLYFROMFILE.lastUploadedPolygons[selectedIndex].coordinates, false, false);
            }
        } catch (e) {
            EDR.WEBGEOCODER.logError('drawSelectedCanvasPreview(): ' + e.message);
        }

        if (redrawGrid) {
            // remove previous grid entries
            $("#polygonPreviewGrid div").remove();

            // add grid entries for the last uploaded polygons
            EDR.POLYFROMFILE.lastUploadedPolygons.forEach((poly, polyIndex) => {

                var getArea = (polygon) => {
                    var googleArray = polygon.coordinates.map(coord => new google.maps.LatLng(coord[1], coord[0]));
                    var areaInMeters = google.maps.geometry.spherical.computeArea(googleArray);
                    var areaInFeet = (areaInMeters * 10.7639104); 	// convert to sq feet
                    var cvtTo = EDR.EDRMapV2.PolygonUtilities.UnitOfAreaMeasurementEnum.SQUAREMILES;
                    return EDR.EDRMapV2.PolygonUtilities.convertPolygonAreaFromSquareFeet(areaInFeet, cvtTo);
                }

                $("#polygonPreviewGrid").append(`
                <div id="polygonPreviewRow${polyIndex}" class='polygonPreviewRow${(polyIndex == selectedIndex ? " selectedItem" : "")}${(!poly.valid ? " invalid" : "")}'> 
                    <i class="fa fa-check" aria-hidden="true"></i>
                    <div id="polygonPreviewInfo${polyIndex}" class="polygonPreviewInfo">
                        <div class="polygonPreviewIcon">
                            <canvas id="polygonPreviewCanvas${polyIndex}" width="90" height="90"></canvas>
                            <div>${poly.valid ? "<b>Area:</b> " + getArea(poly) + " sq mi" : ""}</div>
                        </div>
                        <div class="polygonPreviewText">
                            ${!poly.valid ? "<div class='error>'>" + poly.validationMessage + "</div>" : ""}
                            ${PropertiesToArrayOfKeyValueObjects(poly.properties)
                                .filter(keyValue => propertyFilter(keyValue.key, keyValue.value))
                                .sort(propertySort)
                                .map(keyValue => `<div><b>${keyValue.key}:</b> ${keyValue.value}</div>`)
                                .join("")
                            }
                        </div>
                    </div>
                </div>`
                );
                if (poly.valid) {
                    // add the click event to select this feature
                    $("#polygonPreviewRow" + polyIndex).click(function (e) {
                        if (EDR.POLYFROMFILE.currentFeatureIndex != polyIndex) {
                            var previousFeatureIndex = EDR.POLYFROMFILE.currentFeatureIndex;
                            EDR.POLYFROMFILE.currentFeatureIndex = polyIndex;
                            EDR.POLYFROMFILE.drawSelectedCanvasPreview(false, false, previousFeatureIndex);
                        }
                    });
                }
            });
            document.getElementById("polygonPreviewGrid").scrollTop = 0;
        } else {
            if (typeof previousSelectedRow !== 'undefined')
                document.getElementById("polygonPreviewRow" + previousSelectedRow).className = "polygonPreviewRow";
            document.getElementById("polygonPreviewRow" + selectedIndex).className = "polygonPreviewRow selectedItem";
        }

        EDR.POLYFROMFILE.lastUploadedPolygons.forEach((poly, polyIndex) => {
            var polyCanvas = document.getElementById('polygonPreviewCanvas' + polyIndex);
            var polyMetrics = EDR.POLYFROMFILE.getPreviewMapMetrics(polyCanvas, poly.boundingBox);
            EDR.POLYFROMFILE.drawPreviewPolysOnCanvas([poly], polyCanvas, polyMetrics, selectedIndex == polyIndex ? 0 : -1);
        });

        if (scrollToSelectedRow) {
            var selectedPreviewRow = document.getElementById("polygonPreviewRow" + selectedIndex);
            var baseRow = document.getElementById("polygonPreviewRow0");
            if (selectedPreviewRow && baseRow) {
                var offsetTop = selectedPreviewRow.offsetTop - baseRow.offsetTop;
                console.log({ offsetTop });
                document.getElementById("polygonPreviewGrid").scrollTop = offsetTop;
            }
        }
    },
    getPolygonsFromData: function (data) {
        ///<summary> Creates an array of features based on a geojson input. </summary>
        const TILE_SIZE = 256;
        var polygons = [];

        // the unsupported features appear at the bottom of the list
        var sortPolygons = function () {
            polygons = polygons.sort((poly1, poly2) => poly1.valid == poly2.valid ? 0 : poly1.valid ? -1 : 1);
        }

        // converts a lat long to a google map x y
        var worldProject = function(latLng) {
            var siny = Math.sin((latLng.lat() * Math.PI) / 180);

            // Truncating to 0.9999 effectively limits latitude to 89.189. This is
            // about a third of a tile past the edge of the world tile.
            siny = Math.min(Math.max(siny, -0.9999), 0.9999);

            return new google.maps.Point(
                TILE_SIZE * (0.5 + latLng.lng() / 360),
                TILE_SIZE * (0.5 - Math.log((1 + siny) / (1 - siny)) / (4 * Math.PI))
            );
        };

        // adds a bounding box for the polygon which will be used to display it
        var addBoundingBoxes = function () {
            for (i = 0; i < polygons.length; i++) {
                polygons[i].boundingBox = EDR.POLYFROMFILE.getBoundingBox(polygons[i].worldCoords);
            }
        };

        var addWorldCoordinates = function () {
            for (i = 0; i < polygons.length; i++) {
                polygons[i].worldCoords = polygons[i].coordinates.map(c => worldProject(new google.maps.LatLng(c[1], c[0])))

                // The worldCoordsSortedLinesegments is an array of each line segment in the polygon.
                // The line segments are represented by arrays of two points of world coordinates.
                // It is crucial to sort these two points where the x-coordinate of index 0 is less than
                // the x-coordinate of index 1. Clicks events on the preview map will be tested to be in the span
                // of the width of these line segments with this assumption.
                polygons[i].worldCoordsSortedLinesegments = polygons[i].worldCoords.map((vertex1, i, array) => {
                    return [vertex1, array[(i == 0 ? array.length : i) - 1]].sort((v1, v2) => v1.x - v2.x);
                });
            }
        };

        var validatePolygons = function () {
            polygons.forEach(polygon => {
                if (polygon.geometryType != 'polygon') {
                    switch (polygon.geometryType) {
                        case 'linestring':
                            polygon.validationMessage = 'This shape is a line and not supported for upload. Please upload a polygon.';
                            break;
                        case 'point':
                            polygon.validationMessage = 'This shape is a point and not supported for upload. Please upload a polygon.';
                            break;
                        default:
                            polygon.validationMessage = 'This shape is not supported for upload. Please upload a polygon.';
                            break;
                    }
                    polygon.valid = false;
                } else if (polygon.coordinates.length < 3) {
                    polygon.validationMessage = `This polygon is missing points required to draw a boundary.`;
                    polygon.valid = false;
                } else if (polygon.coordinates.filter(c => c[0] > 180 || c[0] < -180 || c[1] > 90 || c[1] < -90).length > 0) { // TODO look for max lat long as defined constants
                    polygon.validationMessage = `The location is not valid.`;
                    polygon.valid = false; //one known case of this is a shapefile without a projection contains non lat lon geometry
                } else {
                    polygon.valid = true;
                }
            });
        };
                
        considerGeometry = (geometry, properties) => {
            const geometryType = new String(geometry.type).toLowerCase();

            switch (geometryType) {
                case 'geometrycollection':
                    geometry.geometries.forEach(g => considerGeometry(g, properties)); 
                    break;
                case 'polygon':
                    if (Array.isArray(geometry.coordinates)) {
                        geometry.coordinates.forEach(coordinates => {
                            polygons.push({ properties, coordinates, geometryType });
                        });
                    }
                    break;
                case 'linestring':
                    if (Array.isArray(geometry.coordinates)) {
                        var lastPt = geometry.coordinates[geometry.coordinates.length - 1];
                        var firstPt = geometry.coordinates[0];
                        if (Array.isArray(lastPt) && Array.isArray(firstPt) && lastPt.length > 1 && firstPt.length > 1) {
                            if ((lastPt[0] != firstPt[0] || lastPt[1] != firstPt[1])) {
                                // TODO consider adding this code which could close linestrings?
                                // if (lastPt to firstPt is snappably close)
                                // {
                                // console.log("Adding first point copy to the end of the coordinates");
                                //  geometry.coordinates.push(firstPt.slice());
                                // }
                            } else {
                                console.log("Closed linestring detected");
                            }
                        }
                    }
                    polygons.push({ properties, coordinates: geometry.coordinates, geometryType });
                    break;
                case 'point':
                    polygons.push({ properties, coordinates: [geometry.coordinates], geometryType });
                    break;
                default:
                    console.log(`unhandled geometryType ${geometryType}`);
                    console.log({ geometry });
                    polygons.push({ properties, coordinates: geometry.coordinates, geometryType });
                    break;
            }
        }

        var considerFeatures = function(features) {
            if (Array.isArray(features)) {
                features
                    .filter(feature => typeof feature.geometry != 'undefined' && feature.geometry != null)
                    .map(feature => considerGeometry(feature.geometry, feature.properties));
            }
        };

        var considerFeaturesParent = function(featuresParent) {
            if (typeof (featuresParent) != 'undefined' && featuresParent != null)
                if (Array.isArray(featuresParent))
                    featuresParent.map(features => considerFeatures(features));
                else
                    considerFeatures(featuresParent.features);
        };

        var considerData = function(d){
            considerFeaturesParent(d);
            if (typeof (d) != 'undefined' && d != null && Array.isArray(d.layers))
                considerFeaturesParent(d.layers);
        };

        if (Array.isArray(data))
            data.map(d => considerData(d));
        else
            considerData(data);

        validatePolygons();
        addWorldCoordinates();
        addBoundingBoxes();
        sortPolygons();
        return polygons;
    },
    filesToGeoJson: function (files) {
        ///<summary> This is where a user file enters the PolyFromFile. </summary>
        EDR.POLYFROMFILE.getGeometriesPromise(files).then(geometriesArray => {
            if (files.length > 1) {
                console.log({ evtTime: new Date(), error:"Multiple Files not allowed.", files });
                EDR.WEBGEOCODER.displayKMLErrorMessage("Please select only one file. If the error persists, contact us.");
                EDR.WEBGEOCODER.hideFileBrowseAnimation();
            } else {
                var polygonsArray = [];
                if (geometriesArray.length > 0) {
                    polygonsArray = EDR.POLYFROMFILE.getPolygonsFromData(geometriesArray);
                }

                if (polygonsArray.length > 0) {
                    // close the parcel info window if open
                    if (EDR.WEBGEOCODER.parcelInfoWindow != null) {
                        EDR.WEBGEOCODER.parcelInfoWindow.remove();
                    }

                    EDR.POLYFROMFILE.currentFeatureIndex = polygonsArray.findIndex(poly => poly.valid);
                    if (EDR.POLYFROMFILE.currentFeatureIndex >= 0) {
                        document.getElementById('btnProcessFile').removeAttribute("disabled");
                    }

                    EDR.POLYFROMFILE.lastUploadedPolygons = polygonsArray;
                    var boundingBox = EDR.POLYFROMFILE.mergeBoundingBoxes(EDR.POLYFROMFILE.lastUploadedPolygons.filter(poly => poly.valid).map(poly => poly.boundingBox));
                    EDR.POLYFROMFILE.previewMapMetrics = EDR.POLYFROMFILE.getPreviewMapMetrics(document.getElementById('allPolygonPreviewCanvas'), boundingBox);

                    var filename = files[0].name;
                    filename = filename.replace(/^.*[\\\/]/, '');
                    document.getElementById('lblFileName').innerHTML = filename;

                    // change the state of the upload dialog to show the selected file
                    $("#divFilePreview").show();
                    $("#divFileUpload").hide();

                    // reset the flag that any polygons were drawn from a previous file
                    EDR.POLYFROMFILE.drewPreviewPolygon = false;


                    // update the preview with the default selection
                    EDR.POLYFROMFILE.drawSelectedCanvasPreview(true, false);
                } else {
                    EDR.WEBGEOCODER.displayKMLErrorMessage("We were unable to access a polygon from the file. Please check that the file includes a complete polygon and upload again.  If the error persists, contact us.");
                }

                EDR.WEBGEOCODER.hideFileBrowseAnimation();
            }
        }).catch(error => {
            console.log({ evtTime: new Date(), error });
            EDR.WEBGEOCODER.displayKMLErrorMessage("We were unable to access geometry data from the file. Please make sure it is a KML, KMZ or ZIP file containing ShapeFile data.  If the error persists, contact us.");
            EDR.WEBGEOCODER.hideFileBrowseAnimation();
        });
    },
    mergeBoundingBoxes: function (arrayOfBoundingBoxes) {
        ///<summary> Given multiple bounding boxes, returns an all encompassing one </summary>
        var boundingBox = {
            minmin: [
                Math.min(...arrayOfBoundingBoxes.map(bb => bb.minmin[0])),
                Math.min(...arrayOfBoundingBoxes.map(bb => bb.minmin[1])),
            ],
            maxmax: [
                Math.max(...arrayOfBoundingBoxes.map(bb => bb.maxmax[0])),
                Math.max(...arrayOfBoundingBoxes.map(bb => bb.maxmax[1])),
            ]
        };
        boundingBox.midmid = [
            (boundingBox.maxmax[0] + boundingBox.minmin[0]) / 2,
            (boundingBox.maxmax[1] + boundingBox.minmin[1]) / 2,
        ];
        return boundingBox;
    },
    getBoundingBox: function (arrayOfXYObjects) {
        ///<summary> Creates a bounding box used to determine the scale and center pt of the preview thumbnails </summary>
        var boundingBox = {
            minmin: [
                Math.min(...arrayOfXYObjects.map(obj => obj.x)),
                Math.min(...arrayOfXYObjects.map(obj => obj.y))
            ],
            maxmax: [
                Math.max(...arrayOfXYObjects.map(obj => obj.x)),
                Math.max(...arrayOfXYObjects.map(obj => obj.y))
            ]
        };
        boundingBox.midmid = [
            (boundingBox.maxmax[0] + boundingBox.minmin[0]) / 2,
            (boundingBox.maxmax[1] + boundingBox.minmin[1]) / 2,
        ];
        return boundingBox;
    },
    getGeometriesPromise: function (files) {
        const jszip = new JSZip();
        const getExtension = function (fileName) {
            return fileName.split(".").pop();
        }

        var childPromises = [];

        for (let i = 0; i < files.length; i++) {
            var file = files[i];
            var childPromise = new Promise((childResolve, childReject) => {
                if (/^kml$/i.test(getExtension(file.name))) {
                    var reader = new FileReader();
                    reader.addEventListener('loadend', (e) => {
                        const text = e.srcElement.result;
                        const parsedDOM = new DOMParser().parseFromString(text);
                        try {
                            const tjKml = tj.kml(parsedDOM);
                            childResolve(tjKml);
                        } catch (err) {
                            childReject(err);
                        }
                    });
                    reader.readAsText(file);
                } else if (getExtension(file.name) === "geojson" || getExtension(file.name) === "json") {
                    var reader = new FileReader();
                    reader.addEventListener('loadend', (e) => {
                        const text = e.srcElement.result;
                        childResolve(JSON.parse(text));
                    });
                    reader.readAsText(file);
                } else {
                    jszip.loadAsync(file).then(zip => {
                        var kmlDom = null;
                        if (Object.keys(zip.files) == 0) {
                            childReject("No entries for zip files")
                        } else if (Object.keys(zip.files).findIndex(key => /\.kml$/i.test(key) || /\.shp$/i.test(key)) < 0) {
                            childReject("Zip file has no shp or kml entry.");
                        } else {
                            zip.forEach(async (relPath, fileDoc) => {
                                if (/\.kml$/i.test(relPath) && kmlDom === null) {
                                    kmlDom = await fileDoc.async("string");
                                    childResolve(tj.kml(new DOMParser().parseFromString(kmlDom)));
                                } else if (/\.shp$/i.test(relPath)) {
                                    let reader = new FileReader();
                                    reader.onload = function (event) {
                                        var arrayBuffer = event.target.result;
                                        shp(arrayBuffer).then(geometry => childResolve(geometry));
                                    };
                                    reader.readAsArrayBuffer(file);
                                }
                            });
                        }
                    }).catch(error => childReject(error));
                }
            });
            childPromises.push(childPromise);
        }
        return Promise.all(childPromises);
    }

};


// when the document is ready, add a mouse click handler on the preview map that selects a polygon
$(document).ready(function() {
    $("#allPolygonPreviewCanvas").click(function (e) {
        // determine the click location relative to the preview map canvas
        var mouseX = e.pageX - $("#allPolygonPreviewCanvas").offset().left;
        var mouseY = e.pageY - $("#allPolygonPreviewCanvas").offset().top;

        // determine if a polygon was clicked on, and if so, select it
        var index = EDR.POLYFROMFILE.hitTestPreviewMap(EDR.POLYFROMFILE.lastUploadedPolygons, mouseX, mouseY, EDR.POLYFROMFILE.previewMapMetrics);
        if (index >= 0 && EDR.POLYFROMFILE.currentFeatureIndex != index) {
            var previousFeatureIndex = EDR.POLYFROMFILE.currentFeatureIndex;
            EDR.POLYFROMFILE.currentFeatureIndex = index;
            EDR.POLYFROMFILE.drawSelectedCanvasPreview(false, true, previousFeatureIndex);
        }
    });
    $("#allPolygonPreviewCanvas").mousemove(function (e) {
        // determine the click location relative to the preview map canvas
        var mouseX = e.pageX - $("#allPolygonPreviewCanvas").offset().left;
        var mouseY = e.pageY - $("#allPolygonPreviewCanvas").offset().top;
        var selectedIndex = EDR.POLYFROMFILE.currentFeatureIndex;
        var canvas = document.getElementById('allPolygonPreviewCanvas');

        // determine if the mouse is over a polygon and if so highlight it and show the pointing cursor
        var index = EDR.POLYFROMFILE.hitTestPreviewMap(EDR.POLYFROMFILE.lastUploadedPolygons, mouseX, mouseY, EDR.POLYFROMFILE.previewMapMetrics);
        if (index >= 0 && EDR.POLYFROMFILE.currentFeatureIndex != index) {
            $("#allPolygonPreviewCanvas").css('cursor', 'pointer');
            EDR.POLYFROMFILE.drawPreviewPolysOnCanvas(EDR.POLYFROMFILE.lastUploadedPolygons.filter(poly => poly.valid), canvas, EDR.POLYFROMFILE.previewMapMetrics, selectedIndex, index);
        } else {
            $("#allPolygonPreviewCanvas").css('cursor', 'auto');
            EDR.POLYFROMFILE.drawPreviewPolysOnCanvas(EDR.POLYFROMFILE.lastUploadedPolygons.filter(poly => poly.valid), canvas, EDR.POLYFROMFILE.previewMapMetrics, selectedIndex);
        }
    });
});
