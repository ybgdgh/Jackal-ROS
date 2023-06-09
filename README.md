# Jackal-ROS

1. fix the problem of the odom tf frame during the mapping
2. add the frontier-based exploration part
3. add the rrt exploration part, and update the regions of local and global random points detector that can automatically follow the robot position and the centrod of the graph points.
4. multi-robot exploration is developing.




06.06.2023
For fixing multi-robot setting:
1. add the namespace of the group and the tf_prefix for each robot, and send the name as value:
    ```
  <group ns="/robot_1">
      <param name="tf_prefix" value="robot_1" />
      <include file="$(find jackal_gazebo)/launch/spawn_jackal.launch">
        <arg name="x" value="0" />
        <arg name="y" value="0" />
        <arg name="z" value="0.0" />
        <arg name="yaw" value="0" />
        <arg name="config" value="$(arg config)" />
        <arg name="joystick" value="$(arg joystick)" />
        <arg name="robot_name" value="robot_1"/>
      </include>
      <include file="$(find jackal_navigation)/launch/include/multi_map_move.launch">
        <arg name="robot_name" value="robot_1"/>
      </include> 
  </group>

    ```
    The tf_prefix will add all the frames of the robot and gazebo, so we don't need to add them specially.

2. send the robot_name to each launch file, and set it as the name of spawn_robot
    ```
    <!-- Load Jackal's description, controllers, and teleop nodes. -->
    <include file="$(find jackal_description)/launch/description.launch">
        <arg name="config" value="$(arg config)" />
        <arg name="robot_name" value="$(arg robot_name)" />
    </include>
    <include file="$(find jackal_control)/launch/control.launch" >
        <arg name="robot_name" value="$(arg robot_name)" />
    </include>
    <include file="$(find jackal_control)/launch/teleop.launch">
        <arg name="joystick" value="$(arg joystick)" />
    </include>

    <!-- Spawn Jackal -->
    <node name="spawn_$(arg robot_name)" pkg="gazebo_ros" type="spawn_model"
            args="-urdf -model sp_$(arg robot_name) -param robot_description -x $(arg x) -y $(arg y) -z $(arg z) -R 0 -P 0 -Y $(arg yaw)" >
    </node>
    ```

3. In the description.launch file, add the namespace parameter in the robot_description para:
    ```
    <param name="robot_description"
            command="$(find jackal_description)/scripts/$(arg env_runner)
                        $(find jackal_description)/urdf/configs/$(arg config)
                        $(find xacro)/xacro $(find jackal_description)/urdf/jackal.urdf.xacro
                        --inorder 'namespace:=$(arg robot_name)'"/>
    ```

    it's very important that only you add the namespace to xacro (check next step), you can get the corrent sensor topic name and frame name.

4. The most important part for the Gazebo URDF files based on the namespace in **robot_description**:
   add the namespace to **jackal_description/urdf/jackal.gazebo** file, which is used to send the name to xacro file:
   ```
    <gazebo>
    <plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">
        <robotNamespace>/$(arg namespace)</robotNamespace>
    </plugin>
    </gazebo>
    ```
   add the namespace in the sensor xacroused in Gazebo, such as the lmsl lidar, find the xacro file:
    ```
    <xacro:sick_lms1xx frame="${prefix}_laser" topic="${topic}" robot_namespace="$(arg namespace)" />
    ```

5. For the jackal_control/launch/control.launch, set the **base_frame_id** parameter in the controller  configuration as mentioned in the diff_drive_controller [documentation](http://wiki.ros.org/diff_drive_controller#Parameters) for  jackal_velocity_controller of jackal in control.yaml
    ```
    base_frame_id: $(arg robot_name)/base_link
    ```
    note that we need to add the subst to let the yaml file read the namespace:
    ```
    <rosparam command="load" file="$(find jackal_control)/config/control.yaml" subst_value="true"/>
    ```

6. Because we use the **tf_prefix** to set the robot frame, gmapping is not supported, so we need to special the gmapping frame name. Note that we need to set the absolute frame name to avoid the influence of tf_prefix:
   ```
    <launch>
        <arg name="robot_name"/>

        <arg name="scan_topic" default="$(eval optenv('JACKAL_LASER_TOPIC', 'front/scan'))" />

        <node pkg="gmapping" type="slam_gmapping" name="slam_gmapping" output="screen">

            <param name="odom_frame" value="/$(arg robot_name)/odom"/>
            <param name="base_frame" value="/$(arg robot_name)/base_link"/>
            <param name="map_frame" value="/$(arg robot_name)/map"/>
        ...
    </launch>
    ```