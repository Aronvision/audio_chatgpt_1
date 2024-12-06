# audio_chatgpt/audio_chatgpt_node.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import openai
import os

class AudioChatGPTNode(Node):
    def __init__(self):
        super().__init__('audio_chatgpt_node')

        # OpenAI API 키 설정
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if openai.api_key is None:
            self.get_logger().error('OpenAI API 키가 설정되지 않았습니다. 환경 변수 OPENAI_API_KEY를 설정하세요.')
            rclpy.shutdown()
            return

        # STT 결과를 구독
        self.subscription = self.create_subscription(
            String,
            'stt_result',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # ChatGPT 응답을 퍼블리시할 퍼블리셔
        self.publisher_ = self.create_publisher(String, 'chatgpt_response', 10)

        # 길 안내 완료를 알리는 퍼블리셔 추가
        self.route_guidance_publisher = self.create_publisher(String, 'route_guidance_done', 10)

        self.get_logger().info('Audio ChatGPT Node가 시작되었습니다.')

        # 시스템 메시지 설정
        self.system_message = (
            "당신은 병원 안내 로봇입니다. 사람들은 정보성 질문이나 길 안내 질문을 할 수 있습니다. "
            "정보성 질문에 대해서는 적절한 답변을 제공하세요. "
            "길 안내 질문의 경우, 응급실, 수납 및 접수 장소, 편의점, 화장실로의 안내만 가능합니다. "
            "다른 장소에 대한 길 안내 요청에는 '서비스를 준비중입니다'라고 답변하세요."
        )

        # 대상 장소 리스트 정의
        self.target_locations = ['응급실', '수납', '접수', '편의점', '화장실']

    def listener_callback(self, msg):
        stt_text = msg.data
        self.get_logger().info(f'STT 결과 수신: "{stt_text}"')

        # OpenAI API에 요청 보내기
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': self.system_message},
                    {'role': 'user', 'content': stt_text}
                ]
            )
            chatgpt_reply = response['choices'][0]['message']['content'].strip()
            self.get_logger().info(f'ChatGPT 응답: "{chatgpt_reply}"')

            # 응답을 퍼블리시
            reply_msg = String()
            reply_msg.data = chatgpt_reply
            self.publisher_.publish(reply_msg)

            # 사용자의 질문에 대상 장소가 포함되어 있는지 확인하고 장소 이름 추출
            matched_location = None
            for location in self.target_locations:
                if location in stt_text:
                    matched_location = location
                    break

            if matched_location:
                # 길 안내 답변 완료 토픽 퍼블리시
                guidance_msg = String()
                # 예를 들어, guidance_msg.data에 장소 이름 포함
                guidance_msg.data = matched_location
                self.route_guidance_publisher.publish(guidance_msg)
                self.get_logger().info(f'{matched_location}에 대한 길 안내 답변 완료 메시지를 퍼블리시했습니다.')

        except Exception as e:
            self.get_logger().error(f'OpenAI API 요청 중 오류 발생: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = AudioChatGPTNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
