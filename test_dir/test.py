from google.protobuf import text_format, message
import audio_conf_pb2

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


input = '''topic_conf {
  audio_data_topic_name: "/apollo/sensor/microphone"
  audio_detection_topic_name: "/apollo/audio_detection"
  localization_topic_name: "/apollo/localization/pose"
  audio_event_topic_name: "/apollo/audio_event"
  perception_topic_name: "/apollo/perception/obstacles"
}
respeaker_extrinsics_path: "/apollo/modules/audio/conf/respeaker_extrinsics.yaml"'''

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # with open("./audio_conf.pb.txt") as f:
    b = audio_conf_pb2.AudioConf
    # text_format.MessageToString(b)

    text_format.Parse(input, b)
    print()
