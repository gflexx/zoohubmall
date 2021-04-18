$(document).ready(function(){
  var endPoint = $('.endpoint');
  var chartMethod = 'GET';
  
  var productNames = [];
  var productViews = [];

  $.ajax({
    method: chartMethod,
    url: endPoint.val(),
    success: function(data){
      productNames = data.productNames;
      productViews = data.productViews;
      console.log(productViews);
      console.log(productNames);
      setChart();
    },
    error: function(error_data) {
      console.log();
    }
  })

  function setChart(){
  	var productViews = document.getElementById('product-views');
    var productViewsChart = new Chart(productViews, {
      type: 'bar',
      data: {
        labels: productNames,
        datasets: [{
            label: "Product Views",
            fill: true,
            lineTension: 0.3,
            borderColor: 'rgba(75, 192, 192, 1)',
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            data: productViews,
          }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }
      }
    });
    
    
  }

})
