/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


var serverUrl1 = 'https://tools.ladbrokes.com/dashboard/cqm2';

angular.module('genericD3Module',['nvd3','tableModule'])




.controller('controllerDownload', function($http) {

    window.tt = {}
    var init = function() {
        // $http({method:'GET',url:'http://10.33.20.14:9051/api/json?p=' + project_id}).then(function success(response) {
        $http({method:'GET',url: serverUrl1 + '/api/services/' + project_id}).then(function success(response) {

            
            window.tt['services'] = response.data;
            window["environments"].apply(null, [tt]); 

            
        });

        $http({method:'GET',url: serverUrl1 + '/api/tibco/'}).then(function success(response) {
            window.tt['tibco'] = response.data;

            window["monitoring_status"].apply(null, [tt]);    
            

            angular.forEach(queue, function(a,b) {

                // console.log(b);
            // window[a].apply(null, [tt]);
                
            });
        });


        
        
    }

    init();
})


.controller('singleDataController', function($http, $attrs, $scope, $rootScope){

    var jsonSource = $attrs.jsonSource;
    var selectField = $attrs.selectField;
    var filterFields = $attrs.filterFields;

    
    if (filterFields != undefined) {
        filterFields = JSON.parse(filterFields.replace(/'/g, '"'));
        // console.log("selectFields=");   
        // console.log(filterFields[0]);
    }

    if (selectField != undefined)
        selectField = JSON.parse(selectField.replace(/'/g, '"'));

    $scope.result = [];


    $http({method:'GET', url: serverUrl1 +  '/api/' + jsonSource}).then(function success(response) {

        $scope.result = response.data;
        // $scope.select = $scope.result[1];
        // $scope[selectField] = $scope.select;

        if (selectField != undefined && selectField != null) {

            

            if (typeof selectField[1] == "string") {
                $rootScope[selectField[0]] = ($scope.result[ $scope.result.length - 1 ][selectField[1]]).toString();
            }
          /*  else if (typeof selectField[1] == "number") {
                $rootScope[selectField[0]] = ($scope.result[selectField[1]]).toString();
                console.log(($scope.result[selectField[1]]));


            }*/

            var found = [];



            if (filterFields != undefined ) {

                for (var j = 0; j < $scope.result.length; j++) {

                    var entry = $scope.result[j];
                    var match = true;

                    for (var i = 0; i < filterFields.filter.length; i++) {
                        var filter = filterFields.filter[i];

                        // console.log(entry);
                        if ( entry[filter.name].indexOf(filter.value) == -1)
                            match = false;
                        
                    }

                    if (match)
                        found.push(entry);
                }


                /*found = found.filter(function(d) {
                    for (var i = 0; i < filterFields.filter.length; i++) {
                        var item = filterFields.filter[i];

                        if (!item.name in d)
                            return d;

                        return d[item.name].indexOf(item.value) != -1;
                    }
                });*/

                // console.log("found=");
                // console.log(found);

                $rootScope[selectField[0]] = found[found.length - 1][selectField[1]].toString();

            }


            // console.log('selectField');
            // console.log(selectField);
            // console.log(selectField[0]);
            // console.log(selectField[1]);
            // console.log(($scope.result[0][selectField[1]]).toString());
           
        }



    }, function error(response) {});

    // console.log("singleDataController result");
    // console.log($scope.result);


})

.controller('tableController', function($scope, $http, $attrs)  {

   function sortByKey(array, key) {
        return array.sort(function(a, b) {
            var x = a[key]; var y = b[key];
            return ((x < y) ? -1 : ((x > y) ? 1 : 0));
        });
    }

    var filterFields = $attrs.filterFields;

    var limit = $attrs.limit;


    
    if (filterFields != undefined) {
        filterFields = JSON.parse(filterFields.replace(/'/g, '"'));
        console.log("selectFields=");   
        console.log(filterFields.filter);


    }



    var init = function() {

        var link = $attrs.jsonSource;
        // console.log(link);

        $http({method:'GET',url: serverUrl1 + '/api/' + link}).then(function success(response) {

            var array = [];
            // var headers = $attrs.col.split(",");
            var headers = $attrs.col;

            headers = JSON.parse(headers.replace(/'/g, '"'));

            // $scope.sortBy = headers[1];
            $scope.sortReverse = true;

			var labels=[];
            if ($attrs.labelHeaders != undefined)
                // var labels = $attrs.labelHeaders.split(",");
				{
					labels= $attrs.labelHeaders;
                 labels = JSON.parse(labels.replace(/'/g, '"'));
				}
            
         

            if (response.data != undefined && response.data.length > 0)
                response.data.forEach( function(element, index) {
                    

                    var obj = Object();
                    for (i = 0; i < headers.length; i++) {
                        if (labels[i] == undefined || labels[i] == "")
                            obj[headers[i]] = element[headers[i]];
                        else
                            obj[labels[i]] = element[headers[i]];
                    }
                    
                    array.push(obj);
                });

            // console.log("sorting=" + $attrs.sortBy);
            if ($attrs.sortBy != undefined && $attrs.sortBy != "") {
                array = sortByKey(array, $attrs.sortBy);
            }
            // array = sortByKey(array, 'date');
            // array = sortByKey(array, 'Date');
        

            array = array.filter(function(d) {
                for (var i = 0; i < filterFields.filter.length; i++) {
                    var item = filterFields.filter[i];
                    return d[item.name].indexOf(item.value) != -1;
                }
            });


            if (limit != undefined) {
                array = array.slice(0, limit);
            }

            $scope.data = array;




           /* $scope.data=[{name:'reza',id:22,family:'ab'}, {name:'Al',id:29,family:'ka'},{name:'sam',id:30,family:'re'}];*/
            
        }, function error(response) { /*console.log("err: " + response); */});
    }


  

   init($scope);
 
})


.controller('svnSummaryController', function($scope,$http, $attrs) {

    var jsonSource = $attrs.jsonSource;
    $scope.total = "0";

    $http({method:'GET',url: serverUrl1 + '/api/' + jsonSource}).then(function success(response) {
        $scope.total = response.data.total;
    }, function error(response) { });

})

/*.controller('jenkinsJobListController', function($scope, $http, $attrs, $rootScope) {



    $http({method:'GET',url:'http://10.33.20.14:8055/api/jenkins/job/1'}).then(function success(response) {
        $scope.jenkinsJobList = response.data;

        // $scope.chooseJenkinsJob = $scope.jenkinsJobList[0].alias;
        $rootScope.chooseJenkinsJob = $scope.jenkinsJobList[0].alias;



    }, function error(response) { 
        console.log("err: " + response); 
    });



})
*/
.controller('totalTripleJenkinsController', function($scope, $http, $attrs) {

    $scope.totalToday = "0";
    $scope.total7Days = "0";
    $scope.total14Days = "0";

    var jsonSource = $attrs.jsonSource;
    // console.log(jsonSource);
    

    $http({method:'GET',url: serverUrl1 + '/api/' + jsonSource}).then(function success(response) {
        var data = response.data;

        for (var item in data) {
            switch (data[item].period) {
                case 1:
                    $scope.totalToday = data[item].total;
                break;

                
                case 7:
                    $scope.total7Days = data[item].total;
                break;
                

                case 14:
                    $scope.total14Days = data[item].total;
                break;
            }
        }

    }, function error(response) { 
        // console.log("err: " + response); 
    });

})

.controller('chartController',function($scope,$http, $attrs, $timeout)
{

    $scope.showXAxisDate=true;
    $scope.showLegend=false;
    $scope.jsonSource = $attrs.jsonSource;
    
    $scope.useCustomTickValues=false;
    $scope.xAxisFormatType='All';
    $scope.data=[];
    $scope.tickValues=[];
    $scope.options={};
    $scope.options.chart={};
    $scope.options.chart.margin={};



    $scope.options={
     chart: {
                type: 'stackedAreaChart',//stackedAreaChart // multiBarChart
                height: 350,
                margin : {
                    top: 20,
                    right: 20,
                    bottom: 65,
                    left: 50
                },
                showLegend: false,
                area: true,
                clipEdge: false,
                stacked: true,
                headerEnabled: true,
                tooltip: {
                              contentGenerator: function(d) {/*console.log(d);*/ return '<table><thead><tr><td colspan="3"><strong class="x-value">' + d3.time.format('%d/%m/%Y')(new Date(d.data.x)) + '</strong></td></tr></thead><tbody><tr><td class="legend-color-guide"><div style="background-color: ' + d.series[0].color + ';"></div></td><td class="key">' + d.series[0].key + '</td><td class="value">' + d.series[0].value + '</td></tr></tbody></table>'; 
                          }
                        },



                

                useInteractiveGuideline: false,
                interpolate:'monotone',
                x: function(d){
                                  return d.x; },
                y: function(d){ return d.y; },
                       
                xAxis: {
                axisLabel: 'Date',
                tickValues:$scope.tickValues,



                tickFormat: function(d,i) {

                   
                  
            
                  value=d;

                    if($scope.xAxisFormatType=='Even' && ( (new Date(d).getDate()) % 2) == 1)
                    {   
                       

                          value= "";
                    }
                    else if($scope.xAxisFormatType=='Odd' && ( (new Date(d).getDate()) % 2) == 0)
                    {

                          value= "";
                    }
                    if($scope.showXAxisDate  && value!="")
                    {
                            return d3.time.format('%d/%m/%Y')(new Date(d));
                    }

                   return value;
                                             
                    },
                    rotateLabels: 30,
                    showMaxMin:false,
                },

                yAxis: {
                    axisLabel: 'Value ',
                    showMaxMin:false,
                    axisLabelDistance: -10,
                    tickFormat: function(d){
                        return d3.format('.02f')(d);
                    }

                },

                interactiveLayer: {
                    tooltip: { 
                        headerFormatter: function (d) {
                            return d;    
                        },
                    }
                }
            
            }
       };
     
    $scope.init=function(chartType,height,xAxisFormatType, jsonSource){
       $scope.options.chart.height=height;
       $scope.options.chart.type=chartType;
       $scope.xAxisFormatType=xAxisFormatType;
       $scope.getData(jsonSource);

       
    }

    $scope.getData=function(jsonSource)
    {
        
        
        

        $http({method:'GET',url: serverUrl1 +  '/api/' + jsonSource}).then(function success(response)
        {
            // console.log($scope.jsonSource);
          
            $scope.setData(response.data);
            // console.log(response);
        },function fail(response){
            
            // console.log(response);
        } );

       /* $http({method:'GET',url:'http://10.33.20.14:8055/api/' + 'jenkins/chart/deploy/1/14'}).then(function success(response)
        {
            console.log($scope.jsonSource);
          
            $scope.setData(response.data);
            console.log(response);
        },function fail(response){
            
            console.log(response);
        } );
*/
    
    };
    
    $scope.useCustomTickValues=true;
    $scope.setData = function(array1)
    {
        var chartData=[];
       
        for(var i in array1.reverse())
         {
             
             item=array1[i];
                     
              
             chartData.push({key:item.key,values:item.data,area:true});
         }
          $scope.data=chartData; 
         if($scope.useCustomTickValues)
     {
        angular.forEach($scope.data[0].values,function(item)
        {
            $scope.tickValues.push(item.x);
        });
       
     }
    }

 
        /*Random Data Generator */
        function sinAndCos() {
            var sin = [],sin2 = [],
                cos = [];

            //Data is represented as an array of {x,y} pairs.
            for (var i = 0; i < 100; i++) {
                sin.push({x: i, y: Math.sin(i/10)});
                sin2.push({x: i, y: i % 10 == 5 ? null : Math.sin(i/10) *0.25 + 0.5});
                cos.push({x: i, y: .5 * Math.cos(i/10+ 2) + Math.random() / 10});
            }

            //Line chart data should be sent as an array of series objects.
            return [
                {
                    values: sin,      //values - represents the array of {x,y} data points
                    key: 'Sine Wave', //key  - the name of the series.
                    color: '#ff7f0e'  //color - optional: choose your own line color.
                },
                {
                    values: cos,
                    key: 'Cosine Wave',
                    color: '#2ca02c'
                },
                {
                    values: sin2,
                    key: 'Another sine wave',
                    color: '#7777ff',
                    area: true      //area - set to true if you want this line to turn into a filled area chart.
                }
            ];
        };
});
