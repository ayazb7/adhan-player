import 'package:flutter/material.dart';
import 'package:dartssh2/dartssh2.dart';
import 'dart:convert';

void main() => runApp(AdhanControllerApp());

class AdhanControllerApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Adhan Controller',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: HomePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool isMuted = false;
  double volume = 50.0;
  SSHClient? _client;

  @override
  void initState() {
    super.initState();
    _initializeSSHClient();
  }

  @override
  void dispose() {
    _disconnectSSHClient();
    super.dispose();
  }

  Future<void> _initializeSSHClient() async {
    final socket = await SSHSocket.connect('192.168.0.151', 22);
    _client = SSHClient(
      socket,
      username: 'pi',
      onPasswordRequest: () => 'Ayazbaig2002',
    );
    _fetchInitialVolume();
  }

  Future<void> _disconnectSSHClient() async {
    _client?.close();
  }

  Future<void> _fetchInitialVolume() async {
    try {
      final result = await _runSSHCommand('amixer get Master');
      final currentVolume = _parseVolume(result);
      setState(() {
        volume = currentVolume;
      });
    } catch (e) {
      print('Error fetching initial volume: $e');
    }
  }

  double _parseVolume(String amixerOutput) {
    final regex = RegExp(r'\[(\d+)%\]');
    final match = regex.firstMatch(amixerOutput);
    if (match != null) {
      return double.parse(match.group(1)!);
    }
    return 50.0;
  }

  Future<String> _runSSHCommand(String command) async {
    if (_client == null) {
      throw Exception('SSH client is not initialized.');
    }

    final result = await _client!.run(command);
    return utf8.decode(result);
  }

  void _toggleMute() async {
    String command = isMuted ? '/home/pi/Desktop/adhan-player/unmute.sh' : '/home/pi/Desktop/adhan-player/mute.sh';
    String resultMessage;
    try {
      final result = await _runSSHCommand('bash $command');
      resultMessage = isMuted ? 'Unmuted successfully' : 'Muted successfully';
      setState(() {
        isMuted = !isMuted;
      });
      print(result);
    } catch (e) {
      resultMessage = 'Error: $e';
    }

    print(resultMessage);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(resultMessage),
      ),
    );
  }

  void _setVolume(double newVolume) async {
    String resultMessage;
    try {
      final result = await _runSSHCommand('amixer set Master ${newVolume.toInt()}%');
      resultMessage = 'Volume set to ${newVolume.toInt()}%';
      setState(() {
        volume = newVolume;
      });
      print(result);
    } catch (e) {
      resultMessage = 'Error: $e';
    }

    print(resultMessage);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(resultMessage),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Adhan Controller'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: _toggleMute,
              child: Text(isMuted ? 'Unmute Adhan' : 'Mute Adhan'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                textStyle: TextStyle(fontSize: 18),
              ),
            ),
            SizedBox(height: 20),
            Text(
              'Volume: ${volume.toInt()}%',
              style: TextStyle(fontSize: 18),
            ),
            Slider(
              value: volume,
              min: 0,
              max: 100,
              divisions: 100,
              label: volume.toInt().toString(),
              onChanged: (double value) {
                setState(() {
                  volume = value;
                });
              },
              onChangeEnd: (double value) {
                _setVolume(value);
              },
            ),
          ],
        ),
      ),
    );
  }
}
