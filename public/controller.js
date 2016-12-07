angular.module('myApp', []).
	controller('myAppCtrl', ['$scope', '$http',  function($scope, $http) {
		console.log('controller ready');

		$scope.send = function(){ 
			console.log('clicked');
			$http.get('/xml').success(function(response) {
				console.log(response);
        $scope.xml = response;
			});
		}
	}]);