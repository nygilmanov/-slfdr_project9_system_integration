import numpy as np
import cv2
import tensorflow as tf
from styx_msgs.msg import TrafficLight
import rospy

# UNKNOWN=4, GREEN=2, YELLOW=1, RED=0 from TrafficLight msg.

DETECTION_THRESHOLD = 0.5

LABEL_DICT = {1: [TrafficLight.GREEN, 'Green'],
              2: [TrafficLight.RED, 'Red'], 
              3: [TrafficLight.YELLOW, 'Yellow'],
              4: [TrafficLight.UNKNOWN, 'Unknown']}

class TLClassifier():
    def __init__(self, model_path):
        self.detection_graph = self.__load_graph(model_path)
        self.image_tensor = self.detection_graph.get_tensor_by_name("image_tensor: 0")
        self.detection_boxes = self.detection_graph.get_tensor_by_name("detection_boxes:0")
        self.detection_scores = self.detection_graph.get_tensor_by_name("detection_scores:0")
        self.detection_classes = self.detection_graph.get_tensor_by_name("detection_classes:0")
        self.num_detections = self.detection_graph.get_tensor_by_name("num_detections:0")

    def get_classification(self, image):
       
        image = np.expand_dims(image, axis=0)
        
        with tf.Session(graph=self.detection_graph) as sess:
            boxes, scores, classes, num_detections = sess.run([self.detection_boxes, self.detection_scores, self.detection_classes, 
                                                               self.num_detections], feed_dict={self.image_tensor: image})
            print(num_detections)
        
        scores = np.squeeze(scores)
        classes = np.squeeze(classes)
        
        # The result are descending order
        score = scores[0]
        label = classes[0]

        if score > DETECTION_THRESHOLD:
            majority_vote = int(label)
        else:
            majority_vote = 4

        print(LABEL_DICT[majority_vote][1], score)
        return LABEL_DICT[majority_vote][0]
    
    def __load_graph(self, graph_file):
        """Loads a frozen inference graph"""
        graph = tf.Graph()
        with graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(graph_file, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        return graph
