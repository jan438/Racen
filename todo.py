        bzcurve1 = self.mycircle(x,y,radius,direction,startangle,smooth)
        g.add(bzcurve1)
        return g
        
Anticlock
          
1e cp1  30°    self.x - 0.134 * radius  mycircle(300.0, 400.0, 100.0, -1, 0, 3)
         self,y + 0.5 *radius
2e cp2 60°   self x - 0.5 * radius, 
          self.y + 0.866 * radius 

1e cp1  120°    self.x - 0.5 * radius
         self,y - 0.134 *radius
2e cp2 150°   self x - 0.866 * radius, 
          self.y + 0.5 * radius    

1e cp1  210°    self.x + 0.134 * radius
         self,y - 0.5 *radius
2e cp2 240°   self x + 0.5 * radius, 
          self.y - 0.866 * radius    

 1e cp1  300°    self.x + 0.5 * radius
         self,y + 0.134 * radius
2e cp2 330°   self x +  0.866 * radius, 
          self.y + 0.5 * radius
                                     
Clock
          
1e cp1  60°    self.x + 0.5 * radius
         self,y - 0.134 *radius
2e cp2 30°   self x + 0.866 * radius, 
          self.y - 0.5 * radius 

1e cp1  150°    self.x + 0.134 * radius
         self,y + 0.5 *radius
2e cp2 120°   self x + 0.5 * radius, 
          self.y + 0.866 * radius    

1e cp1  240°    self.x - 0.5 * radius
         self,y + 0.134 *radius
2e cp2 210°   self x - 0.866 * radius, 
          self.y + 0.5 * radius    

 1e cp1  330°    self.x - 0.134 * radius
         self,y - 0.5 * radius
2e cp2 300°   self x - 0.5 * radius, 
          self.y - 0.866 * radius
                                                                         
                                     
