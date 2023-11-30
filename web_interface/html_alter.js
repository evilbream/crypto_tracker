
let last_gap
let notify_gap

let markets = function (data) {
    for (let i = 0; i < data.length ; i++){
    let new_row = document.createElement('td');
    new_row.setAttribute('width', 150)
    new_row.setAttribute('align', 'center')
    new_row.setAttribute('bgcolor', '#b2bec3')
    new_row.innerText = data[i];
    document.getElementById('headTable').appendChild(new_row);
    }
    }

    //markets(['Kraken', 'Deepcoin', 'finex', 'Gap'])

 let pairs = function (data) {
    let new_row = document.createElement('tr');
    new_row.setAttribute('id', data[0])
    document.getElementById('mainTable').appendChild(new_row);
    for (let i = 0; i < data.length ; i++){
    let new_row = document.createElement('td');
    let individual_tag = `${data[0]}${i}`
    // console.log(individual_tag)
    new_row.setAttribute('id', individual_tag);
    new_row.setAttribute('width', 150);
    new_row.setAttribute('style', 'font-family: Arial;');
    if (isNaN(data[i])) {
    new_row.setAttribute('bgcolor', '#fff')
    new_row.setAttribute('style',  'font-family: Arial;');
    }
    new_row.innerText = data[i];
    document.getElementById(data[0]).appendChild(new_row);
    }
    }


 let alter_data = function(data){
 element_tag = document.getElementById(`${data[0]}0`)
 if (element_tag){

 for (let i = 0; i < data.length ; i++){
    let tag_text = document.getElementById(`${data[0]}${i}`)
    if (i !== 0 && last_gap[i] < data[i]) {
    tag_text.setAttribute('style', 'color: green;');
    }
    else if (i !== 0 && last_gap[i] > data[i]){
    tag_text.setAttribute('style', 'color: red;');}
    tag_text.innerText = data[i]
 }
 }

 else {pairs(data)}
 }


const websocket = new WebSocket('ws://localhost:8001/')
websocket.addEventListener('message', ({data}) =>{
    const event = JSON.parse(data);
    console.log(event.name);
    if (event.name === 'market'){
        notify_gap = event.notify_gap
        event.markets.push('Gap');
        markets(event.markets);
    }
    else if (event.name === 'pair'){
        console.log(event.pair);
        alter_data(event.pair);
        last_gap = event.pair;
    }
    else {console.log(event);}

    // create markets and currency pairs rows
    //document.write(event[0].name);
});




