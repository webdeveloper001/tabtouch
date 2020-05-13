const server = require('http').createServer(),
	io = require('socket.io')(server);

class AxionWebSocketServer {

	constructor() {
		this.PORT = 35775;
	}

	run() {
		console.log(`Starting server`);
		this.setupWebsocket();
	}

	setupWebsocket() {
		io.on('connection', (client) => this.socketioOnConnection(client));

		server.listen(this.PORT);
		console.log(`Server running! ${this.PORT}`);
	}

	clientIp(client) {
  		return client.request.connection.remoteAddress.substring(7);
	}

	socketioOnConnection(client) {
		client._data = Object.seal({});

		client.on('disconnect', () =>{
			console.log('disconnect');
		});

		client.on('init', (data) => {		
			console.log('init')
		});

		client.on('scrapy', (data) => {		
			io.emit('scrapy', {res: data, time: new Date().toLocaleString()})
		});

		console.log("New Connection from: " + this.clientIp(client));
	}
}

const axionSocketServer = new AxionWebSocketServer();

axionSocketServer.run();
