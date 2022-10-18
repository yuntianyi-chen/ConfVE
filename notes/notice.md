1. How are the configuration files loaded?
- Good news:For planning module, we don't need to build it every time we configure the options.
- By storing this preference outside the code in the form of a configuration file, you can directly adjust the navigation search results without recompiling the code.


2. /modules/xxx/common/xxx_gflags.cc


3. Motivating example
- Try to configure the routing module for testing
- Reflect the change of configuration files on Testing

- (Routing map need to be generated every time changing the configuration file in the routing module since the options are routing map related. Once the routing map is generated, the turning type is determined.)


4. After creating new maps, restart dreamview to load it in the dreamview settings

5. default settings of routing module
- Failed to load default routing. Please make sure the file exists at /apollo/modules/map/data/demo_final_default_cycle_routing.txt
- Failed to load default POI. Please make sure the file exists at /apollo/modules/map/data/demo_final/default_end_way_point.txt

6. 车辆选择后，程序会把会把 calibration/data 目录下对应的车型参数和传感器内外参文件拷贝到作用目录下。

7. change the node name in replay_perception.py if meet some errors
- node = cyber.Node("perception_2")

8. Graph package in the routing module seems to be used in the navigation mode. Not triggered during simulation.

9. Dreadview, Routing (Planning, Prediction) modules have to be relaunched every time we modify the routing configurations since the routing map have to be reloaded.

10. Input and Output of each module
- routing
  - Routing Module for processing input

  - Input
      Map data
      Routing request (Start and end location)

  - Output
      Routing navigation information

