

Date.prototype.addDays = function(days) {
    var dat = new Date(this.valueOf())
    dat.setDate(dat.getDate() + days);
    return dat;
}

 window.getDates = function(startDate, stopDate) {
    var dateArray = new Array();
    var currentDate = startDate;
    while (currentDate <= stopDate) {
        dateArray.push( new Date (currentDate) )
        currentDate = currentDate.addDays(1);
    }
    return dateArray;
}


var formatDate = function(d){
    var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var date = d.getDate() + " " + month[d.getMonth()];
    var time = (d.getHours() < 10 ? "0":"" ) + d.getHours() + ":" + (d.getMinutes()<10?'0':'') + d.getMinutes();
    return (date + " " + time); 
}

var formatDate2 = function(d){
    var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var date = d.getDate() + " " + month[d.getMonth()];
    //var time = d.getHours() + ":" + (d.getMinutes()<10?'0':'') + d.getMinutes();
    return (date); 
}

var formatDate3 = function(d){
    //var month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    var month = d.getMonth() + 1;
    month = (month < 10 ? '0' + month : month);


    var day = d.getDate();
    day  = (day < 10 ? '0' + day : day)
    var date = d.getFullYear() + "-" + month + "-" + day;
    //var time = d.getHours() + ":" + (d.getMinutes()<10?'0':'') + d.getMinutes();
    return (date); 
}
