import 'dart:io';

void main() async {
  String command = '/opt/homebrew/bin/sshpass -p Ayazbaig2002 /usr/bin/ssh pi@192.168.0.151 bash /home/pi/Desktop/adhan-player/unmute.sh';
  try {
    print('Executing command: $command');
    ProcessResult result = await Process.run('bash', ['-c', command]);

    if (result.exitCode == 0) {
      print('Command executed successfully');
      print('Output: ${result.stdout}');
    } else {
      print('Failed to execute command');
      print('Error: ${result.stderr}');
    }
  } catch (e) {
    print('Error: $e');
  }
}
