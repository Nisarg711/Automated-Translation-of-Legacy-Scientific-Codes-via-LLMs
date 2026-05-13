c
c Simulation of velocity vs. time for a bicyclist
c        - Euler or 2nd order Runge-Kutta
c Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
c
      program bicycle2
c
c       Declare the arrays we will need
c
      dimension t(5003), velocity(5003)
      real mass
c
c       Use subroutines to do the work
c
      call initialize(t,velocity,dt,power,mass,nmax,c,area,density,
     c      	lsym,nsym,method)   
      call calculate(t,velocity,dt,power,mass,nmax,c,area,density,
     c      	lsym,nsym,method)   
      call display(t,velocity,dt,power,mass,nmax,c,area,density,
     c      	lsym,nsym,method)
      stop
      end
c
      subroutine initialize(t,velocity,dt,power,mass,nmax,
     c      	c,area,density,lsym,nsym,method)
c
c       Initialize variables
c
      dimension t(*),velocity(*)
      real mass
      character ans,yes
      yes='y'
      print *,'Euler (1) or Runge-Kutta (2)? -> '
      read(5,*) method
      if(method.ne.1.and.method.ne.2) then
      	print *,'must select 1 or 2 ..'
      	stop
      endif
      print *,'initial velocity -> '
      read(5,*) velocity(1)
      t(1) = 0
      print *,'time step -> '
      read(5,*) dt 
      print *,'max time -> '
      read(5,*) tmax
      nmax=min(int(tmax/dt),5000)
      print *,'constant power -> '
      read(5,*) power
      mass = 70
      c = 0.5
      area = 0.33
      density = 1.29
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
      subroutine calculate(t,v,dt,power,mass,nmax,c,area,density,
     c      	lsym,nsym,method)
      real mass,f
c
c       Now use the Euler method or the Runge-Kutta (2nd order)
c
      dimension t(*),v(*)
      if(method.eq.1) then
      	do 10 i = 1,nmax-1
      	v(i+1)=v(i)+dt
     c      		*f(v(i),power,mass,c,density,area)
      	t(i+1) = t(i) + dt
10      	continue
      else
      	do 30 i = 1,nmax-1
      	v1=v(i)+0.5*dt*f(v(i),power,mass,c,density,area)
              v(i+1)=v(i)+dt*f(v1,power,mass,c,density,area)
      	t(i+1) = t(i) + dt
30      	continue
      endif
      return
      end
c
      function f(v,p,x,c,rho,a)
      f=(p/v-c*rho*a*v**2)/x
      return
      end
c
      subroutine display(t,velocity,dt,power,mass,nmax,c,area,density,
     c      	lsym,nsym,method)
c
c       Modified to write simple text output to "graph.out" for comparison.
c
      dimension t(*),velocity(*)
      real mass
      
      open(unit=19, file='graph.out', status='unknown')
      write(19, *) 'Time(s)           Velocity(m/s)'
      do 10 i = 1, nmax
      	write(19, *) t(i), velocity(i)
10      continue
      close(19)
      
      print *, 'Data successfully written to graph.out for comparison.'
      
      return
      end