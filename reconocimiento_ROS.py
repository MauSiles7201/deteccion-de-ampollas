#! /usr/bin/python
#cargamos las librerias necesarias para la deteccion del objeto y la comunicacion con ROS
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np

def main():
    rospy.init_node('image_sub')
    pub_sub = PubSub()
    pub_sub.start()
    rospy.spin()

class PubSub(object):

    def __init__(self):
        self.image = None
        self.bridge = CvBridge()
        self.loop_rate = rospy.Rate(1)
        self.pub = rospy.Publisher('/resultado', Image, queue_size=3)

        rospy.Subscriber("/usb_cam/image_raw/", Image, self.callback)

    def callback(self, msg):
        try:
            cv2_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            rospy.sleep(1)
        except e:
            print(e)
        else:
            #posiciones para mostrar el texto en la pantalla
            x = 150
            y = 200
            h = 200
            w = 200

            #hacemos una aclaracion o mejor visualizacion de la imagen a detectar
            src = cv2.medianBlur(cv2_img, 5)
            src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

            #realizamos la deteccion de circulos en la ampolla
            circles = cv2.HoughCircles(src, cv2.HOUGH_GRADIENT, 1, 20, param1=200, param2=10, minRadius=3, maxRadius=5)

            #si detecta circulos en la ampolla, los dibuja y le pone el texto
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i in circles[0,:]:
                    #dibujar circulo
                    cv2.circle(cv2_img, (i[0], i[1]), i[2], (255,255,0), 2)
                    cv2.putText(cv2_img,'Ampolla - Mala', (x,y-5),1,1.5,(255,255,0),2)

            self.image = cv2_img

    def start(self):
        while not rospy.is_shutdown():
            if self.image is not None:
                rospy.loginfo('Publicando Imagen')
                self.pub.publish(self.bridge.cv2_to_imgmsg(self.image))
            self.loop_rate.sleep()


if __name__ == '__main__':
    main()
