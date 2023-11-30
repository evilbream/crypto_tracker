let notify_gap
let last_gap

let markets = function (data) {
    for (let i = 0; i < data.length ; i++){
        let new_row = document.createElement('th');

        new_row.innerText = data[i];
        document.getElementById('headTable').appendChild(new_row);
    }
}

    // markets(['Kraken', 'Deepcoin', 'finex', 'Gap'])


 let pairs = function (data) {
    let new_row = document.createElement('tr');
    new_row.setAttribute('id', data[0])

    document.getElementById('mainTable').appendChild(new_row);

    for (let i = 0; i < data.length ; i++) {
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


 // reload currency pairs
 let alter_data = function(data){
 element_tag = document.getElementById(`${data[0]}0`) // check if currency pair exists
 if (element_tag) {
 // console.log(element_tag);
 // color red if price is down
 for (let i = 0; i < data.length ; i++){
    let tag_text = document.getElementById(`${data[0]}${i}`)
    // color red and green
    if (i !== 0 && last_gap[i] < data[i]) {
        tag_text.innerText = data[i]
        tag_text.setAttribute('style', 'color: green;');

    }
    else if (i !== 0 && last_gap[i] > data[i]){
        tag_text.innerText = data[i]
        tag_text.setAttribute('style', 'color: red;');}

    }
 }

 else {pairs(data)}
 }



// connect websocket
// currency_pair format: [[data_dicts, ...], gap]
// data_dicts format: {name: str, price: float, seller: bool, pair: str}

// market format: {name: market, markets: [market, ...]}
const websocket = new WebSocket('ws://localhost:8001/')
// запрашивать информацию с сервера и десеарелизовать ее
websocket.addEventListener('message', ({data}) =>{
    const event = JSON.parse(data);
    console.log(event.name);
    if (event.name === 'market'){
        notify_gap = event.notify_gap
        event.markets.push('Gap');
        markets(event.markets);
    }
    if (event.name === 'pair'){
        console.log(event.pair);
        alter_data(event.pair);
        last_gap = event.pair;
    }
    else {console.log(event);}

    // create markets and currency pairs rows
    //document.write(event[0].name);
});




