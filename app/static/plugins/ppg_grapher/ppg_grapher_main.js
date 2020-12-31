/*
 * 
 * ----------------- PPG Grapher -------------------
 * 
 * -------------------------------------------------*/
  
  /*
   * Helper function to convert a number to the graph coordinate
   * ----------------------------------------------------------- */
  function convertToGraphCoord(g, num){
    return Math.floor((g.height / 2) * -(num * g.scaleFactor) + g.height / 2);
  }

  /*
   * Constructor for the PlethGraph object
   * ----------------------------------------------------------- */
  function PlethGraph(cid, datacb){
    
    var g             =   this;
    g.canvas_id       =   cid;
    g.canvas          =   $("#" + cid);
    g.context         =   g.canvas[0].getContext("2d");
    g.width           =   $("#" + cid).width();
    g.height          =   $("#" + cid).height();
    g.white_out       =   g.width * 0.01;
    g.fade_out        =   g.width * 0.15;
    g.fade_opacity    =   0.2;
    g.current_x       =   0;
    g.current_y       =   0;
    g.erase_x         =   null;
    g.speed           =   2;
    g.linewidth       =   1;
    g.scaleFactor     =   1;
    g.pause_graph     =   true;
    g.delay           =   8.33;

    g.plethStarted    =   false;
    g.plethBuffer     =   new Array();
    g.cleanBuffer     =   false
    
    //grid width and height
    g.bw              =   g.width ;
    g.bh              =   g.height ;
    //padding around grid
    g.p               =   0;
    // grid step
    g.step            =   24;
    // grid time start on grid item
    g.timeStartFactor =   2;
    // grid time show space
    g.timeStepFactor  =   4;

    g.timeBuffer      =   new Array();

    g.context.font    =   "14px";

    g.lastTime        =   new Date();

    // animation parameter
    g.curr_time       =  Date.now();
    g.last_time       =  Date.now();
    g.elapsed_time    =  0;

    devicePixelRatio = window.devicePixelRatio || 1,
    backingStoreRatio = g.context.webkitBackingStorePixelRatio ||
                        g.context.mozBackingStorePixelRatio ||
                        g.context.msBackingStorePixelRatio ||
                        g.context.oBackingStorePixelRatio ||
                        g.context.backingStorePixelRatio || 1,

    ratio = devicePixelRatio / backingStoreRatio;
    

    var oldWidth = g.canvas[0].width;
    var oldHeight = g.canvas[0].height;

    g.canvas[0].width = oldWidth * ratio;
    g.canvas[0].height = oldHeight * ratio;

    g.canvas[0].style.width = oldWidth + 'px';
    g.canvas[0].style.height = oldHeight + 'px';

    // now scale the context to counter
    // the fact that we've manually scaled
    // our canvas element
    g.context.scale(ratio, ratio);

    
    /*
     * The call to fill the data buffer using
     * the data callback
     * ---------------------------------------- */
    g.fillData = function() {
      if (!g.cleanBuffer) g.plethBuffer = datacb();
      else g.plethBuffer = []
      };

    /*
     * The call to check whether graphing is on
     * ---------------------------------------- */
    g.isActive = function() {
      return !g.pause_graph;
    };

    /*
     * The call to pause the graphing
     * ---------------------------------------- */
    g.pause = function() {
      g.pause_graph = true;
    };

    /*
     * The call to wrap start the graphing
     * ---------------------------------------- */
    g.start = function() {
      g.cleanBuffer = false
      g.pause_graph = false;

      g.start_time = Date.now();
      g.animate();
    };

      /*
     * The call to stop the graphing
     * ---------------------------------------- */
    g.stop = function() {
      g.pause_graph = true;
      g.cleanBuffer = true;
      g.clear()
    }

    /*
     * The call to start the graphing
     * ---------------------------------------- */
    g.animate = function() {
      reqAnimFrame =   window.requestAnimationFrame       ||
                       window.mozRequestAnimationFrame    ||
                       window.webkitRequestAnimationFrame ||
                       window.msRequestAnimationFrame     ||
                       window.oRequestAnimationFrame;
      
      g.curr_time = Date.now();
      g.elapsed_time = g.curr_time - g.last_time;

      // Recursive call to do animation frames
      if (!g.pause_graph) reqAnimFrame(g.animate);

      // update time & draw
      if (g.elapsed_time > g.delay) {
        g.last_time = g.curr_time - (g.elapsed_time % g.delay);

        // We need to fill in data into the buffer so we know what to draw
        g.fillData();

        // Draw the frame (with the supplied data buffer)
        g.draw();
      }
    };

    g.clear = function(){
      g.context.clearRect(0, 0, g.width, g.height);
      g.current_x       =   0;
      g.current_y       =   0;
      g.grid()
    }

    g.grid =  function(){
      g.context.beginPath();
      
      for (var x = 0; x <= g.bw; x += g.step) {
          g.context.moveTo(0.5 + x + g.p, g.p);
          g.context.lineTo(0.5 + x + g.p, g.bh + g.p);
      }

      for (var y = 0; y <= g.bh; y += g.step) {
          g.context.moveTo(g.p, 0.5 + y + g.p);
          g.context.lineTo(g.bw + g.p, 0.5 + y + g.p);
      }
      
      g.context.strokeStyle = "red";
      g.context.stroke();
      g.context.closePath();
    }

    g.checkTime = function (i) {
      if (i < 10) {
        i = "0" + i;
      }
      return i;
    }
    g.getTime = function(n){
      var currentTime = new Date();

      var timestamp = currentTime.getTime() / 1000;
      if ((timestamp - g.lastTime.getTime() / 1000) > 5 ) g.lastTime = new Date(currentTime.getTime());

      var timeArr = new Array();
      for (var k = 0; k < n; k++){
        timeArr.push([g.lastTime.getHours(), 
          g.checkTime(g.lastTime.getMinutes()), 
          g.checkTime(Math.round(g.lastTime.getSeconds() + k + 0.25*g.timeStartFactor))]);
      }
      return timeArr
    };

    g.getTimeArange = function(){
      var timeArr = new Array();
      var dpx = g.step*g.timeStartFactor; //px, delta between x label
      var m = Math.round(g.width / dpx); // number of x label position
      var dt = Math.round(1200.0 / m); // ms, delta time
      for (var i = 1; i < m; i++){
        timeArr.push(i*dt);
      }
      return timeArr
    }

    g.draw = function() {
      // create grid 
      g.grid();
      // Circle back the draw point back to zero when needed (ring drawing)
      g.current_x = (g.current_x > g.width) ? 0 : g.current_x;

      // "White out" a region before the draw point
      for( i = 0; i < g.white_out ; i++){
        g.erase_x = (g.current_x + i) % g.width;
        g.context.clearRect(g.erase_x, 0, 1, g.height);
      }
      
      // "Fade out" a region before the white out region
      for( i = g.white_out ; i < g.fade_out ; i++ ){
        g.erase_x = (g.current_x + i) % g.width;
        if (i == g.white_out) g.context.fillStyle="#0f0";
        else g.context.fillStyle="rgba(255, 255, 255, " + g.fade_opacity.toString() + ")";
        g.context.fillRect(g.erase_x, 0, 1, g.height);

        // Print Time Label (X)
        if (i == g.white_out) { 
          g.context.fillStyle="#fff";
          g.context.fillRect(0, g.height*0.92, g.width, g.height*0.99);
          
          // update start and end time
          var time_width = 0.25*g.width/g.step; // in second
          g.timeBuffer = g.getTime(time_width);
          var y = 0;
          
          for (var x = g.step*g.timeStartFactor; x <= g.bw; x += g.step*g.timeStepFactor) {
            g.context.fillStyle="#000";
            var xx = 0.5 + x + g.p - 20;

            var timePrint = g.timeBuffer[y][0] + ":" + g.timeBuffer[y][1] + ":" + g.timeBuffer[y][2];
            g.context.fillText(timePrint, xx, g.height*0.97);
            y += 1;
          }
        }

      }

      // If this is first time, draw the first y point depending on the buffer
      if (!g.started) {
        g.current_y = convertToGraphCoord(g, g.plethBuffer[0]);
        g.started = true;
      }

      // Start the drawing
      g.context.beginPath();

      g.context.strokeStyle = "black";

      // We first move to the current x and y position (last point)
      g.context.moveTo(g.current_x, g.current_y);

      for (i = 0; i < g.plethBuffer.length; i++) {
        // Put the new y point in from the buffer
        g.current_y = convertToGraphCoord(g, g.plethBuffer[i]);
        
        // Draw the line to the new x and y point
        g.context.lineTo(g.current_x += g.speed, g.current_y);
        
        // Set the 
        g.context.lineWidth   = g.linewidth;
        g.context.lineJoin    = "round";
        
        // Create stroke
        g.context.stroke();
      }
      // Stop the drawing
      g.context.closePath();
    };

    // ------------------------------- draw single sample ------------------------
    g.draw_sample = function() {
      // Create grid
      g.grid();
      // Circle back the draw point back to zero when needed (ring drawing)
      g.current_x = (g.current_x > g.width) ? 0 : g.current_x;
      
      // Print Time Label (X) 
      g.context.fillStyle="#fff";
      g.context.fillRect(0, g.height*0.92, g.width, g.height*0.99);
      
      // update start and end time
      g.timeBuffer = g.getTimeArange();

      var y = 0;      
      for (var x = g.step*g.timeStartFactor; x < g.bw; x += g.step*g.timeStepFactor) {
        g.context.fillStyle="#000";
        g.context.fillText(g.timeBuffer[y], x - 8, g.height*0.97);
        y += 1;
      }

      // If this is first time, draw the first y point depending on the buffer
      if (!g.started) {
        g.current_y = convertToGraphCoord(g, g.plethBuffer[0]);
        g.started = true;
      }
      g.speed = Math.round(g.bw / g.plethBuffer.length) + 0.5;

      for (i = 0; i < g.plethBuffer.length; i++) {
        // Start the drawing
        g.context.beginPath();
        g.context.strokeStyle = "black";

        // We first move to the current x and y position (last point)
        g.context.moveTo(g.current_x, g.current_y);

        // Put the new y point in from the buffer
        g.current_y = convertToGraphCoord(g, g.plethBuffer[i]);
        
        // Draw the line to the new x and y point
        g.context.lineTo(g.current_x += g.speed, g.current_y);
        // Set the 
        g.context.lineWidth   = g.linewidth;
        g.context.lineJoin    = "round";
        
        // Create stroke
        g.context.stroke();
        // Stop the drawing
        g.context.closePath();
      }
    };
  }
