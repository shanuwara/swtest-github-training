/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



/* required version.js */



var module=angular.module('tableModule',[]);

module.filter('switch', function () { 
      return function (input, map) {
          return map[input] || '';
      }; 
  });

module.filter('unique', function() {

  var list = [];
  return function(input, map) {
      input.map(function(d) {

       
        if (list.indexOf(d[map]) == -1) {
          list.push(d[map]);
        }

       
      });
     return list;
  }

});


module.filter('filterMulti', function () { 
      return function (input, map) {
        // console.log("filterMulti");
        console.log(input);
        console.log(map);

        var output = [];

        var keys = Object.keys(map);
        for (i in keys) {

          var item = keys[i];
          
          for (j in input) {
            var entry = input[j];

            for (z in map[item]) {
              var search = map[item][z];
              if (entry[item].indexOf(search) != -1) {
                // output.push(entry);
                return entry;
              }
            }
          }

        }

        console.log(output);
        // return output;
      }; 
  });



module.filter('hideFilter', [function() {
  var ind = 0;
  return function (item,element) {

    // delete item[element];
    var newItem = item;

    console.log(element);
    // delete newItem[element];
    return newItem;

  }
}]);


module.filter('tester', [function() {
  var ind = 0;
  return function (item,element) {

    // delete item[element];
    var newItem = item;

    console.log(element);
    // delete newItem[element];
    return newItem;

  }
}]);


module.directive("cqmCircleCoverage", function($compile) {

  var controller = function($scope, $attrs) {
    $scope.circle = function(value) {

      var container = document.createElement("div");

        if (value == undefined) 
          value = "0";

        value = value.replace("%", "");

        // d3.select("#qualityfour>svg").remove();
        d3.select(container).select("svg").remove();

        var w = 300,                        //width
        h = 300,                            //height
        r = 100,                            //radius
        ir = 50,
        pi = Math.PI,
        //color = d3.scale.category20c();     
         color = d3.scale.linear()
        .domain([0,100])
        .range(["green", "red"]);

     
        var _data = [
                 
                  {"label": value + "%", "value": value, "color": "#58715a", "state": 1}, 
                 {"label": (100 - value) + "%", "value": (100 - value), "color": "#a05e5a", "state":0},

                ];

        console.log(data);

        var data = _data;
        
        // var vis = d3.select("#qualityfour") .append("svg")
        var vis = d3.select(container).append("svg")
            .style("width", "202px")
            .style("height", "110px")
            .data([_data])          
                .attr("width", w)  
                .attr("height", h)
            .append("svg:g")       
                .attr("transform", "translate(" + r + "," + r + ")")    
     
        var arc = d3.svg.arc()              
            .outerRadius(r)
            .innerRadius(ir);
     
        var pie = d3.layout.pie()           
            .value(function(d) { return d.value; })
            .startAngle(-90 * (pi/180))
            .endAngle(90 * (pi/180))
            .sort(null);
     
        var arcs = vis.selectAll("g.slice")     
            .data(pie)                          
            .enter()                            
                .append("svg:g")                
                    .attr("class", "slice");    
     
            arcs.append("svg:path")
                    .attr("fill", function(d, i) { return _data[i].color } ) 
                    .attr("d", arc);                                    
     
            arcs.append("svg:text")                                     
                .attr("text-anchor", "middle")     
                .attr("fill", "white")                     
                .text(function(d, i) { if (_data[i].state == 1 ) return _data[i].label; });   

        return container.innerHTML;     
    
      
    }
  }


  return {
     restrict: 'E',
       scope:{
            datasource:'=',
            percent:'@percent',
            container:'=',
           
       },
       // transclude: true,
       controller:controller,
       controllerAs: 'ctrl',
       link: function (scope, ele, attrs) {


        scope.$watch('percent', function(newData, oldData) {
          if (newData && newData != undefined) {
           
            ele.html(scope.circle(newData) );
            $compile(ele.contents())(scope);
          }

        })


       
     
      }
     }
});



module.directive("cqmCircleDebt", function($compile) {

  var controller = function($scope, $attrs) {

    $scope.circle = function (param, data) {

      var container = param;
      var value = data;

      var container = document.createElement("div");

    /* circle */
      //window.data1 = data2[0]

      if (value == undefined)
        value = "0";

      value = value.replace("%", "");

      var tmp = [{"population": value , "color":"#a05e5a"},
              {"population": (100 - value) ,"color":"#58715a" },
             
              ];
       

        var data2 = [];
        data2.push(tmp);
        data1 = data2[0];

      var arc = d3.svg.arc()
          .outerRadius(40)
          .innerRadius(40 - 15);


      var pie = d3.layout.pie()
        .sort(null)
        .value(function(d) { return d.population; });


        d3.select(container).select("svg").remove();
      var canvas = d3.select(container).append("svg");

      canvas
        .attr("width", 100)
        .attr("height", 100);

      var group = canvas.append("g")
          // .classed("arcs-content", true)
          .attr("transform", "translate(40,40)")

        group
          .append("text")
          .attr("fill", "white")
          .attr("transform", "translate(0,5)")
          .text(value)
          .style("text-anchor", "middle")
          .style("font-size", "14px")
          .style("font-weight", "bold")
          .attr("id", "circle-percent");


        group
          .selectAll("path")
          .data(data1)
          .enter()
          .append("path")
          .style("fill", function(d) { return d.color})
          
          .attr("d", function(d,i) { return arc(pie(data1)[i]); })
          d3.select("#circle-percent")
              .text(function(d,i) { return data1[i].population});
          


       

    /* circle - end */
    console.log(container);
    return container.innerHTML;
   }

   $scope.getPercent = function() {
    return $attrs.percent;
   }



  }

   return {
     restrict: 'E',
       scope:{
            datasource:'=',
            percent:'@percent',
            container:'=',
           
       },
       // transclude: true,
       controller:controller,
       controllerAs: 'ctrl',
       link: function (scope, ele, attrs) {


        scope.$watch('percent', function(newData, oldData) {
          if (newData && newData != undefined) {
           
            ele.html(scope.circle("", newData) );
            $compile(ele.contents())(scope);
          }

        })


       
     
      }
     }


})

module.directive("cqmVersionChart", function() {

  var controller = function($scope, $attrs) {

    console.log("$scope.datasource");
    console.log($scope.datasource);

    $scope.getData = function() {
      return $scope.datasource;
    }

    var data = $scope.getData();
    if (data != undefined && data.length > 0)
    versionChart("#element14", $scope.getData());

   /* $scope.version = $attrs.version;
    console.log("version=" + )*/

  };

    



  return {
     restrict: 'E',
       scope:{
            datasource:'=',
            version:'=',
            container:'=',
           
       },
       transclude: true,
       controller:controller,
       controllerAs: 'ctrl',


    /*template: function(element, attrs) {

      return "<h1>{{getData()}}</h1>";
    }*/
      link: function(scope, element, attrs) {
        scope.$watch('version', function(newData, oldData) {
          if (newData) {
            console.log("version=" + newData);
          }

        })


        scope.$watch('[datasource, version]', function(newData, oldData) {
          if (newData && newData[0].length > 0 && newData[1] != undefined) {
            versionChart(attrs.container, newData[0].filter(function(el) {/*return el.VerName == newData[1]*/
                return el.VersionId == newData[1]
            }));

            

            console.log("newData");
            console.log(newData);
            console.log(attrs.version)
          }

        }, true)
      }
  };

})

module.directive('cqmTable', function() {
  var controller=function($scope)
  {

    // console.log('datasource='+$scope.datasource);
    $scope.sortBy="";
    this.isSortDesc=function(col)
    {
        return ($scope.sortBy==col && $scope.sortReverse);
        
    };
    this.formatColumn=function(value,colFormat)
    {
     /* var colValue=value;
         if(colFormat=='Date')
         {
            colValue=parseInt(value / 3600);
         }*/

         return colValue;
    };
    this.isSortAsc=function(col)
    {
         return ($scope.sortBy==col && !$scope.sortReverse);
    };
    this.isSorting=function(col)
    {
       return ($scope.sortBy!=col);
    };
    $scope.sort=function(col)
    {
     $scope.sortBy=col;
     $scope.sortReverse = !$scope.sortReverse
    };

    $scope.isHideHeaders = function() {

      return !$scope.hideHeaders;
    };

    $scope.isHeadersOnBottom = function() {

      return $scope.bottomHeaders;
    };

    $scope.getColStatus = function() {
      if ($scope.colStatus != undefined) {
        return $scope.colStatus[0];
      }

      return "";
    }

    $scope.getRowStatus = function() {
      if ($scope.rowStatus != undefined) {
        return $scope.rowStatus[0];
      }

      return "";
    }

    $scope.getColStatusSuccessClass = function() {
      if ($scope.colStatus != undefined)
        return $scope.colStatus[1];
      return "";
    }

    $scope.getRowStatusSuccessClass = function() {
      if ($scope.rowStatus != undefined)
        return $scope.rowStatus[1];
      return "";
    }


    $scope.getColStatusFailureClass = function() {
      if ($scope.colStatus != undefined)
        return $scope.colStatus[2];
      return "";
    }

    $scope.getRowStatusFailureClass = function() {
      if ($scope.rowStatus != undefined)
        return $scope.rowStatus[2];
      return "";
    }


    $scope.isStatusCol = function(col, value) {

      if (col == $scope.getColStatus()) {
        if (value == 1)
          return 1;

        if (value == "" || value == 0)
          return 0
      } else 
        return 2;

      
    }

    $scope.isStatusRow = function(item) {

      if ($scope.getRowStatus() != "")
        switch(item[$scope.getRowStatus()]) {
          case 1:
            return 1;
          break;

          case "":
            return 0;
          break;

          case 0:
            return 0;
          break;
        }
      return 2;
    }

    $scope.getTagKey = function() {
      if ($scope.tagKey != undefined)
        return $scope.tagKey;

    }

    $scope.getTagValue = function() {
      if ($scope.tagValue != undefined)
        return $scope.tagValue;
    }

    $scope.getData = function() {

      return $scope.datasource;
    }

    $scope.getFilteredData = function(key, value, sort) {
      
      if ($scope.getData() != undefined) {

        var tmp =  $scope.getData().slice(0);
        for (var i = 0; i < tmp.length; i++) {
          if (tmp[i] != undefined && tmp[i][key] != undefined && tmp[i][key] != value)
            delete tmp[i];
        }
      }


       function sortByKey(array, key) {
        return array.sort(function(a, b) {
            var x = a[key]; var y = b[key];
            return ((x < y) ? -1 : ((x > y) ? 1 : 0));
        });
      }

      if (tmp != undefined && sort != undefined && sort != "") {
        tmp = sortByKey(tmp, sort);
      }



      return tmp;

    }

    $scope.isShowScrollBars = function() {
      if ($scope.showScrollBars == undefined)
        return false;

      return $scope.showScrollBars;
    }

    
  };


  return {
       restrict: 'E',
       scope:{
            datasource:'=',
            sortBy:'=',
            sortByHeader:'=',
            sortReverse:'=',
            hideHeaders:'=',
            bottomHeaders:'=',
            colFormats:'=',
            colStatus:"=",
            rowStatus:"=",
            tagKey:"=",
            tagValue:"=",
            showScrollBars:"=",
    
       },
       controller:controller,
       controllerAs: 'tblCtrl',
       template: function(element, attrs) {
       var html = '<table>' +
       // orderBy:sortBy:sortReverse track by $index
                  '<thead ng-if="isHideHeaders() && isHeadersOnBottom() == false">' +
                    '<tr><th ng-repeat="(col,val) in datasource[0]" sortDir="asc"  ng-class="{\'sorting\': tblCtrl.isSorting(col), \'sorting_asc\': tblCtrl.isSortAsc(col), \'sorting_desc\': tblCtrl.isSortDesc(col)}" ng-click="sort(col)" ng-show="col != getTagKey()"><span>{{col}}</th></tr>' + 
                  '</thead>' +
                  '<tbody style="overflow-y: {{ isShowScrollBars()|switch:{false:\'initial\', true:\'scroll\'} }};" ng-data2="">' + 
                    '<tr ng-repeat="item in (getFilteredData(getTagKey(), getTagValue(), sortByHeader) | orderBy:sortBy:sortReverse) track by $index" ng-tag="{{item[getTagKey()]}}" ng-class="{{isStatusRow(item)}}|switch:{0:getRowStatusFailureClass()};  "><td title="{{v}}" ng-repeat="(k,v) in item" ng-show="k != getTagKey()" ng-class="{{isStatusCol(k,v)}}|switch:{1:getColStatusSuccessClass(), 0:getColStatusFailureClass()} "><span>{{v}}</span></td></tr>' + 
                  '</tbody>' + 
                  '<thead ng-if="isHeadersOnBottom()">' +
                    '<tr><th ng-repeat="(col,val) in datasource[0]" sortDir="asc" ng-class="{\'sorting\': tblCtrl.isSorting(col), \'sorting_asc\': tblCtrl.isSortAsc(col), \'sorting_desc\': tblCtrl.isSortDesc(col)}" ng-click="sort(col)" ng-show="col != getTagKey()"><span>{{col}}</th></tr>' + 
                  '</thead>' +
                '</table>';

               /* var html = '<table>' +
                  '<thead ng-if="isHideHeaders() && isHeadersOnBottom() == false">' +
                    '<tr><th ng-repeat="(col,val) in datasource[0]" sortDir="asc"  ng-class="{\'sorting\': tblCtrl.isSorting(col), \'sorting_asc\': tblCtrl.isSortAsc(col), \'sorting_desc\': tblCtrl.isSortDesc(col)}" ng-click="sort(col)" ng-show="col != getTagKey()"><span>{{col}}</th></tr>' + 
                  '</thead>' +
                  '<tbody>' + 
                    '<tr ng-repeat="item in datasource | orderBy:sortBy:sortReverse track by $index " ng-show="item[getTagKey()] == getTagValue()" ng-tag="{{item.Alias}}" ng-class="{{isStatusRow(item)}}|switch:{0:\'failure\'};  {{item[getTagKey()] == getTagValue() && $even}}|switch:{true:\'even\'}; {{item[getTagKey()] == getTagValue() && $odd}}|switch:{true:\'odd\'}"><td ng-repeat="(k,v) in item" ng-show="k != getTagKey()" ng-class="{{isStatusCol(k,v)}}|switch:{1:\'success\', 0:\'failure\'} "><span>{{v}}</span></td></tr>' + 
                  '</tbody>' + 
                  '<thead ng-if="isHeadersOnBottom()">' +
                    '<tr><th ng-repeat="(col,val) in datasource[0]" sortDir="asc" ng-class="{\'sorting\': tblCtrl.isSorting(col), \'sorting_asc\': tblCtrl.isSortAsc(col), \'sorting_desc\': tblCtrl.isSortDesc(col)}" ng-click="sort(col)" ng-show="col != getTagKey()"><span>{{col}}</th></tr>' + 
                  '</thead>' +
                '</table>';*/

          return html;
       }
  };
    
});
