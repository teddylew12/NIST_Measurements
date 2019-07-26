    /**
     * Created by sdk on 6/27/2018.
     * Custom functions to be used primarily by wafer report
     */

    // typo lol
    // based on name, convert to coordinates for heatmap
    function get_location_on_wafter(chipName) {
        var location = chipName.split("-").pop();
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
    function formatJcData(xs, ys, success) {
        var my_data = [];

        for(var x = 0; x<11;x++) {
            for (var y = 0; y<11; y++) {
                if (xs.includes(x) && ys.includes(y)) {
                    var cell = success.find(function(element) {
                        return element[0] === x && element[1] === y
                    });
                    if (cell === undefined) {
                        my_data.push([x,y,0])
                    }
                    else {
                        my_data.push(cell)
                    }

                }
                else {
                    my_data.push([x,y,0])
                }
            }
        }

        return my_data
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
        console.log("new");
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
        last_y = 0;
        for (var i = 0; i < values_length; i++) {
            var this_val = values[i];

            x = this_val[0];
            y = this_val[1];
            if y>last_y {
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
