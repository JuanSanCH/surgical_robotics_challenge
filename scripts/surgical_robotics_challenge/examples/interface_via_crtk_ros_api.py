# Import the relevant classes
import rospy
from geometry_msgs.msg import TransformStamped, PoseStamped
from sensor_msgs.msg import JointState
from PyKDL import Frame, Rotation, Vector
import time
from enum import Enum

class ArmType(enum.Enum):
    PSM1=1
    PSM2=2
    ECM=3

def frame_to_transform_stamped_msg(frame):
    msg = TransformStamped()
    msg.header = rospy.Time.now()
    msg.transform.translation.x = frame.p[0]
    msg.transform.translation.y = frame.p[1]
    msg.transform.translation.z = frame.p[2]

    msg.transform.rotation.x = Rotation.GetQuaternion()[0]
    msg.transform.rotation.y = Rotation.GetQuaternion()[1]
    msg.transform.rotation.z = Rotation.GetQuaternion()[2]
    msg.transform.rotation.w = Rotation.GetQuaternion()[3]

    return msg

def list_to_sensor_msg_position(jp_list):
    msg = JointState()
    msg.position = jp_list
    return msg

class ARMInteface:
    def __init__(self, arm_type):
        if arm_type == ArmType.PSM1:
            arm_name = '/PSM1'
        elif arm_type == ArmType.PSM2:
            arm_name = '/PSM2'
        elif arm_type == ArmType.ECM:
            arm_name = '/ECM'
        else:
            raise ("Error! Invalid Arm Type")

        self._cp_sub = rospy.Subscriber(arm_name + "/measured_cp", TransformStamped, self.cp_cb, queue_size=1)
        self._jp_sub = rospy.Subscriber(arm_name + "/measured_cp", JointState, self.jp_cb, queue_size=1)
        self.cp_pub = rospy.Publisher(arm_name + "/servo_cp", TransformStamped, queue_size=1)
        self.jp_pub = rospy.Publisher(arm_name + "/servo_jp", JointState, queue_size=1)

        self.measured_cp_msg = None
        self.measured_jp_msg = None

    def cp_cb(self, msg):
        self.measured_cp = msg

    def jp_cb(self, msg):
        self.measured_jp_msg = msg

    def measured_cp(self):
        return self.measured_cp_msg

    def measured_jp(self):
        return self.measured_jp_msg

    def servo_cp(self, pose):
        if type(pose) == Frame:
            msg = frame_to_transform_stamped_msg(pose)
        self.cp_pub.publish(msg)

    def servo_jp(self, jp):
            if type(jp) == list:
                msg =
        self.jp_pub.publish(jp)

class SceneObjectType(Enum):
    Needle=1
    Entry1=2
    Entry2=3
    Entry3=4
    Entry4=5
    Exit1=6
    Exit2=7
    Exit3=8
    Exit4=9

class SceneInterface:
    def __init__(self):
        self._scene_object_poses = {}
        self._scene_object_poses[SceneObjectType.Needle] = None
        self._scene_object_poses[SceneObjectType.Entry1] = None
        self._scene_object_poses[SceneObjectType.Entry2] = None
        self._scene_object_poses[SceneObjectType.Entry3] = None
        self._scene_object_poses[SceneObjectType.Entry4] = None
        self._scene_object_poses[SceneObjectType.Exit1] = None
        self._scene_object_poses[SceneObjectType.Exit2] = None
        self._scene_object_poses[SceneObjectType.Exit3] = None
        self._scene_object_poses[SceneObjectType.Exit4] = None
        self._subs = []

        namespace = '/ambf/env/'
        suffix = '/State/pose'
        for k, i in self._scene_object_poses.items():
            self._subs.append(rospy.Subscriber(namespace + k + suffix, TransformStamped, k, queue_size=1))

    def state_cb(self, msg, key):
        self._scene_object_poses[key] = msg

    def measured_cp(self, object_type):
        return self._scene_object_poses[object_type]

# Create an instance of the client
rospy.init_node('your_name_node')
psm1_sub
time.sleep(0.5)

# Get a handle to PSM1
psm1 = ARMInteface(ArmType.PSM1)
# Get a handle  to PSM2
psm2 = ARMInteface(ArmType.PSM2)
# Get a handle to ECM
ecm = ARMInteface(ArmType.ECM)
# Get a handle to scene to access its elements, i.e. needle and entry / exit points
scene = SceneInterface()
# Small sleep to let the handles initialize properly
time.sleep(0.5)

# To get the pose of objects
print("PSM1 End-effector pose in Base Frame", psm1.measured_cp())
print("PSM1 Base pose in World Frmae", psm1.get_T_b_w())
print("PSM1 Joint state", psm1.measured_jp())
print("---------")
print("PSM2 End-effector pose in Base Frame", psm2.measured_cp())
print("PSM2 Base pose in World Frmae", psm2.get_T_b_w())
print("PSM2 Joint state", psm2.measured_jp())
print("---------")
# Things are slightly different for ECM as the `measure_cp` returns pose in the world frame
print("ECM pose in World", ecm.measured_cp())
print("---------")
# Scene object poses are all w.r.t World
print("Entry 1 pose in World", scene.measured_cp(SceneObjectType.Entry1))
print("Exit 4 pose in World", scene.measured_cp(SceneObjectType.Exit4))

####
#### Your control / ML - RL Code will go somewhere in this script
####

# The PSMs can be controlled either in joint space or cartesian space. For the
# latter, the `servo_cp` command sets the end-effector pose w.r.t its Base frame.
T_e_b = Frame(Rotation.RPY(np.pi, 0, np.pi/2.), Vector(0., 0., -1.0))
print("Setting the end-effector frame of PSM1 w.r.t Base", psm1.servo_cp(T_e_b))
print("---------")
T_e_b = Frame(Rotation.RPY(np.pi, 0, np.pi/4.), Vector(0., -0.2, -1.0))
print("Setting the end-effector frame of PSM2 w.r.t Base", psm2.servo_cp(T_e_b))
print("---------")
# Controlling in joint space
jp = [0., 0., 1.0, 0.5, 0.7, 0.9]
print("Setting PSM1 joint positions to ", jp)
psm1.servo_jp(jp)
jp = [0., 0., 1.0, -0.5, -0.7, -0.9]
print("Setting PSM2 joint positions to ", jp)
psm2.servo_jp(jp)
print("---------")

# The ECM should always be controlled using its joint interface
jp = [0., 0., 0.5, 0.3]
print("Setting ECM joint positions to ", jp)
ecm.servo_jp(jp)


print('END')