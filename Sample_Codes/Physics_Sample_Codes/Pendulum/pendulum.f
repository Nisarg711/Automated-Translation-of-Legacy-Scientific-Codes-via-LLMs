c
c Simulation of non-linear pendulum
c        - Euler or Runge-Kutta (2nd order usual one)
c Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
c
      program pendulum
c
c       Declare the arrays we will need
c
      dimension th(5003),om(5003),t(5003)
c
c       Use subroutines to do the work
c
      call initialize(th,om,t,ext,dt,q,fd,dr,lsym,nsym,method)
      call calculate(th,om,t,ext,dt,q,fd,dr,n,lsym,nsym,method)
      call display(th,om,t,ext,dt,q,fd,dr,n,lsym,nsym,method)
      stop
      end
c
      subroutine initialize(th,om,t,ext,dt,q,fd,dr,lsym,nsym,method)
c
c       Initialize variables
c
      dimension th(*),om(*),t(*)
      character ans,yes
      yes='y'
      print *,'Euler(1), Euler-Cromer(2) or Runge-Kutta(3)? -> '
      read(5,*) method
      if(method.ne.1.and.method.ne.2.and.method.ne.3) then
        print *,'must select 1, 2, or 3 ..'
        stop
      endif
      print *,'initial angle, angular velocity, pendulum length?'
      read(5,*) th(1),om(1),ext
      t(1)=0.0
      print *,'time step, damping const, force amp, frequency?'
      read(5,*) dt,q,fd,dr
      print *,'set line, symbol?'
      read(5,14) ans
14      format(a1)
      if(ans.eq.yes) then
        print *,'lsym, nsym ? -> '
        read(5,*) lsym,nsym
      else
        lsym=-1
        nsym=1
      endif
      return
      end
c
      subroutine calculate(th,om,t,ext,dt,q,fd,dr,n,lsym,nsym,method)
c
c       Now use the Euler method or the Runge-Kutta (2nd order)
c
      dimension th(*),om(*),t(*)
      g=9.8
      period=6.2831853/sqrt(g/ext)
      nmax=5000
      do 10 i = 2,nmax
        t(i) = t(i-1)+dt
          if(method.eq.1) then
        call dv(om(i-1),th(i-1),t(i-1),g,ext,q,fd,dr,dom,dth)
              om(i) = om(i-1)+dt*dom
              th(i) = th(i-1)+dt*dth
          elseif(method.eq.2) then
        call dv(om(i-1),th(i-1),t(i-1),g,ext,q,fd,dr,dom,dth)
              om(i) = om(i-1)+dt*dom
              th(i) = th(i-1)+dt*om(i)
          else
        call dv(om(i-1),th(i-1),t(i-1),g,ext,q,fd,dr,dom,dth)
              om1 = om(i-1)+0.5*dt*dom
              th1 = th(i-1)+0.5*dt*dth
        t1 = t(i-1)+0.5*dt
        call dv(om1,th1,t1,g,ext,q,fd,dr,dom2,dth2)
        om(i)=om(i-1)+dt*dom2
        th(i)=th(i-1)+dt*dth2
          endif
          if(t(i).ge.10.0*period) then
        n=i
        return
          endif
10      continue
      n=nmax
      return
      end
c
      subroutine dv(om0,th0,t0,g,ext,q,fd,dr,dom,dth)
      dth=om0
      dom=-g/ext*sin(th0)-q*om0+fd*sin(dr*t0)
      return
      end
c
      subroutine display(th,om,t,ext,dt,q,fd,dr,n,lsym,nsym,method)
c
c       Modified to write simple text output to "graph.out" for comparison.
c
      dimension th(*),om(*),t(*)
      
      open(unit=19, file='graph.out', status='unknown')
      write(19, *) 'Time(s)           Angle(rad)'
      do 10 i = 1, n
        write(19, *) t(i), th(i)
10      continue
      close(19)
      
      print *, 'Data successfully written to graph.out for comparison.'
      
      return
      end