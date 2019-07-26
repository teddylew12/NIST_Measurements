    /**
     * Created by sdk on 6/27/2018.
     */
    function get_location_on_wafter(chipName) {
        var location = chipName.split("-").pop();
        var x = location.substr(0,1);
        var y = location.substr(1);

        x = x.charCodeAt() - 65;
        y = parseInt(y) - 1;

        return [y,x]

    }

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

    function jcFilterChanged () {
        console.log(this.value);
        return 0
    }

    function find_chip_name(x, y) {
        var location = String.fromCharCode(x+65) +  (y+1).toString();
        return location
    }

    function gotoChip(x,y) {
        var axis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H','I','J','K'];
        var location = axis[y] + String(x);
        var chipname = "{{ wafer.name }}".substr(0,7) + "-" + location + "//All";

        $("#filter_dev").val(chipname);


        $("#chip_form").submit()
    }

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

    function find_average(data) {
        var average = 0;
        for(var i=0;i<data.length;i++){
            average += data[i][1]
        }
        return average/data.length
    }

    function find_Jc(sqrt_ic_data) {
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
        for (var i = 0; i < values_length; i++) {
            var this_val = values[i];

            x = this_val[0];
            y = this_val[1];
            sum_x += x;
            sum_y += y;
            sum_xx += x * x;
            sum_xy += x * y;
            count++;

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
