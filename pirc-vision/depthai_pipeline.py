import depthai as dai
import cv2

class DepthAIPipeline:
    def __init__(self):
        self.pipeline = dai.Pipeline()
        self.setup_pipeline()
    
    def setup_pipeline(self):
        # Color camera
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(640, 640)
        cam_rgb.setInterleaved(False)
        cam_rgb.setColorOrder(dai.ColorOrder.BGR)
        
        # YOLOv10 Neural Network
        nn = self.pipeline.create(dai.node.YoloDetectionNetwork)
        nn.setBlobPath("models/yolo10n.blob")
        nn.setConfidenceThreshold(0.5)
        nn.setNumClasses(80)
        nn.setCoordinateSize(4)
        nn.setAnchors([10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326], False)
        nn.setAnchorMasks({"side80": [0,1,2], "side40": [3,4,5], "side20": [6,7,8]})
        nn.setIouThreshold(0.5)
        
        # Link
        cam_rgb.preview.link(nn.input)
        cam_rgb.setPreviewKeepAspectRatio(False)
        
        xout_rgb = self.pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        cam_rgb.preview.link(xout_rgb.input)
        
        nn_out = self.pipeline.create(dai.node.XLinkOut)
        nn_out.setStreamName("nn")
        nn.out.link(nn_out.input)
