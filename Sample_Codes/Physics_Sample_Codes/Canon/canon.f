c
c Simulation of velocity vs. time for a large cannon
c        - Euler or Runge-Kutta (2nd or 4th order usual ones)
c Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
c
      program cannon2 
c
c       Declare the arrays we will need
c
      dimension x(5003), y(5003)
c
c       Use subroutines to do the work
c
      call initialize(dt,vinit,theta,Am,lsym,nsym,method)   
      call calculate(x,y,dt,vinit,theta,Am,n,method)   
      call display(x,y,n,theta,Am,dt,lsym,nsym,method)
      stop
      end
c
      subroutine initialize(dt,vinit,theta,Am,lsym,nsym,method)
c
c       Initialize variables
c
      character ans,yes
      yes='y'
      print *,'Euler (1) or Runge-Kutta 2nd order (2), 4th (3)? -> '
      read(5,*) method
      if(method.ne.1.and.method.ne.2.and.method.ne.3) then
        print *,'must select 1, 2, or 3 ..'
        stop
      endif
      print *,'initial velocity -> '
      read(5,*) vinit
      print *,'time step -> '
      read(5,*) dt 
      print *,'drag/m -> '
      read(5,*) Am
      print *,'firing angle -> '
      read(5,*) theta
      print *,'set line, symbol?'
      read(5,14) ans
14      format(a1)
      if(ans.eq.yes) then
        print *,'line and symbol numbers -> '
        read(5,*) lsym,nsym
      else
        lsym=-1
        nsym=1
      endif
      return
      end
c
      subroutine calculate(x,y,dt,vinit,theta,Am,n,method)
c
c       Now use the Euler method or the Runge-Kutta (2nd order)
c
      dimension x(*),y(*)
      x(1)=0.0
      y(1)=0.0
      vx=vinit*cos(3.141592*theta/180.0)
      vy=vinit*sin(3.141592*theta/180.0)
      nmax=5000
      if(method.eq.1) then
        do 10 i = 2,nmax
        call deriv(x(i-1),y(i-1),vx,vy,0.0,Am,dx,dy,dvx,dvy)
        x(i)=x(i-1)+dt*dx
        y(i)=y(i-1)+dt*dy
        vx=vx+dt*dvx
        vy=vy+dt*dvy
        if(y(i).le.0.0) then
          n=i
          go to 15
        endif
10        continue
      elseif(method.eq.2) then
        do 30 i = 2,nmax
        call deriv(x(i-1),y(i-1),vx,vy,0.0,Am,dx,dy,dvx,dvy)
        x1=x(i-1)+0.5*dt*dx
        y1=y(i-1)+0.5*dt*dy
        vx1=vx+0.5*dt*dvx
        vy1=vy+0.5*dt*dvy
        call deriv(x1,y1,vx1,vy1,0.0,Am,dx2,dy2,dvx2,dvy2)
        x(i)=x(i-1)+dt*dx2
        y(i)=y(i-1)+dt*dy2
        vx=vx+dt*dvx2
        vy=vy+dt*dvy2
        if(y(i).le.0.0) then
          n=i
          go to 15
        endif
30        continue
      else
        do 40 i = 2,nmax
        call deriv(x(i-1),y(i-1),vx,vy,0.0,Am,dx,dy,dvx,dvy)
        x1=x(i-1)+0.5*dt*dx
        y1=y(i-1)+0.5*dt*dy
        vx1=vx+0.5*dt*dvx
        vy1=vy+0.5*dt*dvy
        call deriv(x1,y1,vx1,vy1,0.0,Am,dx2,dy2,dvx2,dvy2)
        x2=x(i-1)+0.5*dt*dx2
        y2=y(i-1)+0.5*dt*dy2
        vx2=vx+0.5*dt*dvx2
        vy2=vy+0.5*dt*dvy2
        call deriv(x2,y2,vx2,vy2,0.0,Am,dx3,dy3,dvx3,dvy3)
        x3=x(i-1)+dt*dx3
        y3=y(i-1)+dt*dy3
        vx3=vx+dt*dvx3
        vy3=vy+dt*dvy3
        call deriv(x3,y3,vx3,vy3,0.0,Am,dx4,dy4,dvx4,dvy4)
        x(i)=x(i-1)+0.16666667*dt*(dx+2*dx2+2*dx3+dx4)
        y(i)=y(i-1)+0.16666667*dt*(dy+2*dy2+2*dy3+dy4)
        vx=vx+0.16666667*dt*(dvx+2*dvx2+2*dvx3+dvx4)
        vy=vy+0.16666667*dt*(dvy+2*dvy2+2*dvy3+dvy4)
        if(y(i).le.0.0) then
          n=i
          go to 15
        endif
40        continue
      endif
      n=nmax
15      a=-y(n)/y(n-1)
      x(n)=(x(n)+a*x(n-1))/(1+a)
      y(n)=0.0
      return
      end
c
      subroutine deriv(x0,y0,vx0,vy0,t0,Am,dx,dy,dvx,dvy)
      dx=vx0
      dy=vy0
      f=Am*sqrt(vx0**2+vy0**2)
      dvx=-f*vx0
      dvy=-f*vy0-9.8
      return
      end
c
      subroutine display(x,y,nmax,theta,Am,dt,lsym,nsym,method)
c
c       Modified to write simple text output to "graph.out" for comparison.
c
      dimension x(*),y(*)
      
      open(unit=19, file='graph.out', status='unknown')
      write(19, *) 'Distance(m)       Height(m)'
      do 10 i = 1, nmax
        write(19, *) x(i), y(i)
10      continue
      close(19)
      
      print *, 'Data successfully written to graph.out for comparison.'
      
      return
      end