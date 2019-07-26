    /**
     * Created by sdk on 6/27/2018.
     * Custom functions to be used primarily by wafer report
     * Some comments added by Nathan on 6/12/2019
     *
     */

    // typo lol
    // based on name, convert to coordinates for heatmap
    function get_location_on_wafter(chipName) {
        var location = chipName.split("-", 2).pop();
        var x = location.substr(0,1);
        var y = location.substr(1);

        x = x.charCodeAt() - 65;
        y = parseInt(y) - 1;

        return [y,x]

    }

    // highlights the chip in the measured map
    function highlightChip(chipName, color) {
        var location = get_location_on_wafter(chipName);
        var div = $("#measured_chips");
        var index = div.data('highchartsChart');
        var chart = Highcharts.charts[index];
        var data = chart.series[0].data;

        var cell = data.find(function(element) {
            return element.x == location[0] && element.y == location[1]  && element.value == 100
        });

        cell.update({value: 300, color: color}, true);
    }

    // based on a hover in the chip map, highlight the Ic points
    function highlight_series(location) {
        var div = $("#chip_ic");
        var index = div.data('highchartsChart');
        var chart = Highcharts.charts[index];
        var series = chart.series;

        var this_series = series.find(function (element) {
            return element.name.indexOf(location) !== -1
        });

        if (this_series !== undefined) {
            Highcharts.each(series, function (seriesItem) {
                Highcharts.each(['group', 'markerGroup'], function (group) {
                    seriesItem[group].attr('opacity', 0.05);
                });
            });

            this_series['group'].attr('opacity', 1);
            this_series['markerGroup'].attr('opacity', 1);

            return this_series.color
        }
        return '#3b49c4'
    }

    // opposite of above
    function unhighlight_series() {
         var div = $("#chip_ic");
         var index = div.data('highchartsChart');
         var chart = Highcharts.charts[index];
         var series = chart.series;

         Highcharts.each(series, function (seriesItem) {
             Highcharts.each(['group', 'markerGroup'], function (group) {
                 seriesItem[group].attr('opacity', 1);
             });
         });
     }

     // opposite of above
    function unhighlightChip(chipName) {
        var location = get_location_on_wafter(chipName);
        var div = $("#measured_chips");
        var index = div.data('highchartsChart');
        var chart = Highcharts.charts[index];
        var data = chart.series[0].data;

        var cell = data.find(function(element) {
            return element.x == location[0] && element.y == location[1] && element.value == 300
        });

        cell.update({value: 100, color: null});
    }

    // update the jc plot
    function updateJc(data_json, filter) {
        var index = $("#Jc_map").data('highchartsChart');
        var chart = Highcharts.charts[index];

        var filtered_json = filterJson(data_json, "type", filter)
        var chip_names = Object.keys(filtered_json)
        var Jc_array = []


        for (var i=0;i<chip_names.length;i++) {
            var location = get_location_on_wafter(chip_names[i].substr(8));
            location.push(find_Jc(filtered_json[chip_names[i]]) / (100*100*1000));
            Jc_array.push(location)
        }

        var formatted_data = formatJcData(chart.options.xs_array, chart.options.ys_array, Jc_array)
        chart.series[0].setData(formatted_data, true, true, false)

    }

    // format the Jc data (or really any heat map data) correctly
    function formatJcData(xs, ys, success) { //Formats data for the heat map
        var my_data = []; //Initialize empty array
        for(var x = 0; x<12;x++) { //Loop through length/width of wafer
            for (var y = 0; y<12; y++) {
                if (xs.includes(x) && ys.includes(y)) { //If the measured list includes the current x and y
                    var cell = success.find(function(element) { //cell = [x, y, Jcvalue]
                        return element[0] === x && element[1] === y
                    });
                    if (cell === undefined) { //If not cell was found
                        my_data.push([x,y,0]) //add an empty cell to the output data
                    }
                    else {
                        my_data.push(cell) //otherwise append the apropriate cell
                    }

                }
                else {
                    my_data.push([x,y,0]) //If not in the measured list, append an empty cell 
                }
            }
        }
        console.log(my_data) //Print the data to the console
        return my_data //my_data = [[x, y, 0],[x,y,0],...,[x,y,Jcvalue],...]
    }

    //Format average Ic data (for singles wafer reports heat map)
    //Note: In this case, the data is stored in objects instead of arrays because David wanted to be able to display the standard deviation
    function formatIcData(xs, ys, success) {
        var my_data = []; //Initialize empty data array
        for(var x = 0; x<12;x++) { //loop through all x and y of wafer
            for (var y = 0; y<12; y++) {
                if (xs.includes(x) && ys.includes(y)) { //If the measured list includes the current x and y
                    var cell = success.find(function(element) { //get cell = [x, y, Ic_average, st_dev]
                        return element[0] === x && element[1] === y
                    });
                    if (cell === undefined) { //Should never go in here, just to check
                        my_data.push({x:x,y:y,value:0,st_dev:0}) //Add an empty cell to the list of cells
                    }
                    else {
                        my_data.push({x:cell[0], y:cell[1], value:cell[2], st_dev:cell[3]}) //otherwise add the correctly-populated cell to the output
                    }

                }
                else if(!((x === 0 && (y === 0 || y === 1 || y === 2 || y === 9 || y === 10 || y === 11)) || 
                          (x === 1 && (y === 0 || y === 1 || y === 10 || y === 11)) || 
                          (x === 2 && (y === 0 || y === 11)) ||
                          (x === 11 && (y === 0 || y === 1 || y === 2 || y === 10 || y === 11)) ||
                          (x === 10 && (y === 0 || y === 1 || y === 10 || y === 11)) ||
                          (x === 9 && (y === 0 || y === 11)))) {
                    my_data.push({x:x,y:y,value:0,st_dev:0}) //Only add an empty cell to the cells list if it's not one of the 24 corner chips.
                    //This makes the heat map graphic have the shape of a wafer
                }  
            }
        }
        console.log(my_data) //print the data to the console
        return my_data //my_data = [[x, y, 0,0],[x,y,0,0],...,[x,y,Ic_average,st_dev],...] (one 1x4 array for each chip)
    }

    // filter json based on dropdown change
    function filterJson(json, filter, filter_value) {

        // base case - all, do nothing
        if (filter_value === "All") {
            return json
        }


        var keys = Object.keys(json)
        var return_json = {}

        for (var i=0;i<keys.length;i++) {
            var keys2 = Object.keys(json[keys[i]])
            return_json[keys[i]] = {}
            for (var j=0;j<keys2.length; j++) {
                if (json[keys[i]][keys2[j]][filter] === filter_value) {
                    return_json[keys[i]][keys2[j]] = json[keys[i]][keys2[j]]
                }
            }
        }

        return return_json
    }

    // opposite of above
    function find_chip_name(x, y) {
        var location = String.fromCharCode(x+65) +  (y+1).toString();
        return location
    }

    // go to /chip_report and send info needed
    function gotoChip(x,y, waferName) {
        var axis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H','I','J','K'];
        var location = axis[y] + String(x);
        // below could be problematic due to wafer name inconsisyancy
        var chipname = waferName.substr(0,7) + "-" + location + "//All";

        $("#filter_dev").val(chipname);
        $("#chip_form").submit()
    }

    // unused but converts hex to rgba
    function hexToRgbA(hex){
        var c;
        if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
            c= hex.substring(1).split('');
            if(c.length== 3){
                c= [c[0], c[0], c[1], c[1], c[2], c[2]];
            }
            c= '0x'+c.join('');
            return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+',0.3)';
        }
        throw new Error('Bad Hex');
    }

    // finds average in an array
    function find_average(data) {
        var average = 0;
        for(var i=0;i<data.length;i++){
            average += data[i][1]
        }
        return average/data.length
    }

    // finds Jc based on json containing devices to use
    function find_Jc(data) {
        let average = (array) => array.reduce((a,b) => a + b) / array.length;
        var keys = Object.keys(data)
        var total_Jc = 0;
        var count = 0;
        for (var i=0;i<keys.length; i++) {
            if (data[keys[i]]["Ic"].length > 0) {
                var Jc = 0;
                var A = 0;
                A = Math.PI * Math.pow(data[keys[i]]["size"] * 1e-06, 2)
                Jc = average(data[keys[i]]["Ic"]) / A;
                total_Jc += Jc;
                count++;
            }
        }
        if (count === 0) {
            return 0
        }
        return total_Jc/count
    }

    //Finds average Ic for singles chip reports
    function find_Ic_Average(data) {
        let average = (array) => array.reduce((a,b) => a + b) / array.length; //Define an average function
        var keys = Object.keys(data) //get a json with all the devices
        var total_Ic = 0;
        var count = 0;
        for(var i = 0; i < keys.length; i++){ //loop through the devices
            if(data[keys[i]]["Ic"].length > 0) { //If the device has one or more Ic measurements,
                var Ic = 0;
                Ic = average(data[keys[i]]["Ic"]); //find the average of all the Ic measurements
                total_Ic += Ic; //add the average to total_Ic
                count++; //increment the counter
            }
        }
        if(count === 0) { //If no meaurements were taken, return zero
            return 0
        }

        return (1000*total_Ic) / count //Multiply by 1000 for to get the average Ic of the chip in milliamps
    }

    //Finds standard deviation of Ic for singles chip reports (written by Nathan)
    function find_Ic_ST_DEV(data) { //Uses Var(X) = E[X^2]-(E[X])^2 to find ST_DEV(Ic)
        let average = (array) => array.reduce((a,b) => a + b) / array.length; //define an average function
        var keys = Object.keys(data) //get a json with the devices
        var total_Ic = 0;
        var total_Ic2 = 0; //This will be (Ic)^2
        var count = 0;
        for(var i = 0; i < keys.length; i++) { //loop through the devices
            if(data[keys[i]]["Ic"].length > 0) {//if there is one or more measurement for the device
                var Ic = 0;
                Ic = average(data[keys[i]]["Ic"]); //find the average of all Ic measurements for the device
                total_Ic += Ic; //Add the Ic to the total
                total_Ic2 += Math.pow(Ic,2); //Add tje square of the Ic to the total
                count++; //Increment the counter
            }
        }
        if(count === 0) { //If no measurements were taken, return zero
            return 0
        }
        //Uses ST_DEV[Ic] = sqrt(E[(Ic)^2] - (E[Ic])^2)
        var exp_of_Ic2 = total_Ic2 / count; //expected value of the squre of Ic
        var exp_of_Ic_squared = Math.pow((total_Ic / count),2); //(mean of the Ic) squared
        var variance = exp_of_Ic2 - exp_of_Ic_squared; //variance of Ic
        var st_dev = Math.sqrt(variance); //standard deviation of Ic in amps
        return st_dev*1000 //Multiply by 1000 for mA 
    }

    // finds the Jc based on sqrt ic data
    function find_Jc_easy(sqrt_ic_data) {
        var total_Jc = 0;
        var count = 0;
        for (var i=0;i<sqrt_ic_data.length; i++) {
            var Jc = 0;
            var A = 0;
            A = Math.PI * Math.pow(sqrt_ic_data[i][0]*1e-06, 2)
            Jc = Math.pow(sqrt_ic_data[i][1], 2) / A;
            total_Jc+= Jc;
            count++;
        }
        return total_Jc/count
    }

    // linear line of best fit
    function findBestFitLine(values) {
        var sum_x = 0;
        var sum_y = 0;
        var sum_xy = 0;
        var sum_xx = 0;
        var count = 0;

        /*
         * We'll use those variables for faster read/write access.
         */
        var x = 0;
        var y = 0;
        var values_length = values.length;

    //        if (values_length != values_y.length) {
    //            throw new Error('The parameters values_x and values_y need to have same size!');
    //        }

        /*
         * Nothing to do.
         */
        if (values_length === 0) {
            return [ [], [] ];
        }

        /*
         * Calculate the sum for each of the parts necessary.
         */

        // ignores if not increasing, fixes outlier problem
        last_y = 0;
        for (var i = 0; i < values_length; i++) {
            var this_val = values[i];

            x = this_val[0];
            y = this_val[1];
            if (y>last_y) {
                sum_x += x;
                sum_y += y;
                sum_xx += x * x;
                sum_xy += x * y;
                last_y = y;
                count++;
            }



        }

        /*
         * Calculate m and b for the formular:
         * y = x * m + b
         */
        var m = (count*sum_xy - sum_x*sum_y) / (count*sum_xx - sum_x*sum_x);
        var b = (sum_y/count) - (m*sum_x)/count;

        return [m, b]

    //        /*
    //         * We will make the x and y result line now
    //         */
    //        var result_values_x = [];
    //        var result_values_y = [];
    //
    //        for (var v = 0; v &lt; values_length; v++) {
    //            x = values_x[v];
    //            y = x * m + b;
    //            result_values_x.push(x);
    //            result_values_y.push(y);
    //        }
    //
    //        return [result_values_x, result_values_y];
    }
