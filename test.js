const appId = '095caaa73d8d44b99f18e1c82d39775e';
const appSecret = '55f536bbd0054fb79f4764b5dd56628a';
const apiBaseUrl = 'https://apiproxy.telphin.ru';

const userLogin = "SDN26821";
const userPass = 'Anai2fo0';


const apiAuthUrl = apiBaseUrl + '/oauth/authorize';
console.log(apiAuthUrl);
let xmlHttp = new XMLHttpRequest();
xmlHttp.open("GET", apiAuthUrl + '?response_type=code&redirect_uri=' + encodeURIComponent('http://127.0.0.1') + '&scope=all&client_id=' + appId, false ); // false for synchronous request
xmlHttp.send( null );
let postUrl = xmlHttp.responseURL;
//console.dir(xmlHttp);

let body = 'username=' + encodeURIComponent(userLogin) + '&password=' + encodeURIComponent(userPass);
xmlHttp.open("POST", postUrl, false);
xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xmlHttp.withCredentials = true;
xmlHttp.send( body );
alert(xmlHttp.responseText);