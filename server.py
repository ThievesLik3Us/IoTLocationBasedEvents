import json
from klein import Klein

class Events(object):
    app = Klein()

    def __init__(self):
        self.config = {}
        # save off current config
        with open("trigger_event_list.json", "r") as config_file:
            self.config = json.load(config_file)
        with open("trigger_event_list_working_copy.json", "w") as config_file:
            config_file.write(json.dumps(self.config, indent=4, sort_keys=True))

    @app.route('/')
    def events(self, request):
        request.setHeader('Content-Type', 'application/json')
        with open("trigger_event_list_working_copy.json", "r") as config_file:
            self.config = json.load(config_file)
        return json.dumps(self.config, indent=4, sort_keys=True)

    @app.route('/Devices', methods=['PUT'])
    def add_device(self, request):
        request.setHeader('Content-Type', 'application/json')
        body = json.loads(request.content.read())
        with open("trigger_event_list_working_copy.json", "r+") as config_file:
            self.config = json.load(config_file)
            self.config["Bluetooth MAC Addresses"].append(body)
            config_file.seek(0)
            config_file.write(json.dumps(self.config, indent=4, sort_keys=True))
            config_file.truncate()
        return json.dumps({'success': True})

    @app.route('/Devices', methods=['GET'])
    def get_devices(self, request):
        request.setHeader('Content-Type', 'application/json')
        with open("trigger_event_list_working_copy.json", "r") as config_file:
            self.config = json.load(config_file)
        return json.dumps(self.config["Bluetooth MAC Addresses"], indent=4, sort_keys=True)

    @app.route('/<string:name>', methods=['GET'])
    def get_item(self, request, name):
        request.setHeader('Content-Type', 'application/json')
        return json.dumps(self.config.get(name), indent=4, sort_keys=True)

    @app.route('/Events', methods=['PUT'])
    def save_event(self, request, name):
        request.setHeader('Content-Type', 'application/json')
        body = json.loads(request.content.read())
        with open("trigger_event_list_working_copy.json", "r+") as config_file:
            self.config = json.load(config_file)["Events"]
            events = self.config["Events"]
            if(events[name] == None):
                events[name] = body
            else:
                events.append(body)
            self.config["Events"] = events
            config_file.seek(0)
            config_file.write(json.dumps(self.config, indent=4, sort_keys=True))
            config_file.truncate()
        return json.dumps({'success': True})


    @app.route('/Events/<string:name>', methods=['GET'])
    def get_event(self, request, name):
        request.setHeader('Content-Type', 'application/json')
        events = self.config["Events"]
        return json.dumps(events[name], indent=4, sort_keys=True)


if __name__ == '__main__':
    store = Events()
    store.app.run('localhost', 8080)