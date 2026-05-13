c
c Simulation of the Lorenz map
c        - Euler or Runge-Kutta (2nd order usual one)
c Program to accompany "Computational Physics" by N. Giordano and H. Nakanishi
c Line 89 was originally incorrect, corrected to "t1 = t(i-1)+0.5*dt"
c
      program lorenz
c
c       Declare the arrays we will need
c
      implicit real*8 (a-h,o-z)
      dimension x(500003),y(500003),z(500003),t(500003)
c
c       Use subroutines to do the work
c
      call initialize(x,y,z,t,sigma,r,b,dt,lsym,nsym,k,nstep,m,nout)
      call calculate(x,y,z,t,sigma,r,b,dt,lsym,nsym,k,nstep,m)
      if(nout.eq.1) then
          open(1,file='out.lorenz')
          rewind(1)
          do 10 i=1,nstep
              write(1,15) t(i),x(i),y(i),z(i)
10        continue
          close(1)
15        format(1x,1p,4(e12.5,1x))
      else
          call display(x,y,z,t,sigma,r,b,dt,lsym,nsym,k,nstep,m)
      endif
      stop
      end
c
      subroutine initialize(x,y,z,t,sigma,r,b,dt,lsym,nsym,k,n,m,nout)
c
c       Initialize variables
c
      implicit real*8 (a-h,o-z)
      dimension x(1),y(1),z(1),t(1)
      character ans,yes
      yes='y'
      print *,'Lorenz model: Euler (1) or Runge-Kutta [2nd ord] (2)?'
      read(5,*) m
      print *,'parameters: sigma, r, b ?'
      read(5,*) sigma,r,b
      print *,'initial x, y, z ?'
      read(5,*) x(1),y(1),z(1)
      print *,'time step, how many steps ?'
      read(5,*) dt,n
      t(1)=0
      print *,'record output to a file [out.lorenz] ?'
      read(5,14) ans
      if(ans.eq.yes) then
          nout=1
      else
          nout=2
          print *,'plot [z vs t,z vs x](1) or [x , y vs t](2)?'
          read(5,*) k
          if(k.ne.1.and.k.ne.2) then
              print *,'must select 1 or 2 ...'
              stop
          endif
          print *,'set line, symbol?'
          read(5,14) ans
14        format(a1)
          if(ans.eq.yes) then
              print *,'lsym, nsym ? -> '
              read(5,*) lsym,nsym
          else
              lsym=0
              nsym=1
          endif
      endif
      return
      end
c
      subroutine calculate(x,y,z,t,sigma,r,b,dt,lsym,nsym,k,nstep,m)
c
c       Now use Euler or Runge-Kutta (2nd order)
c
      implicit real*8 (a-h,o-z)
      dimension x(1),y(1),z(1),t(1)
      nstep=min(nstep,500000)
      if(m.eq.2) then
         do 10 i = 2,nstep
          t(i) = t(i-1)+dt
          call dv(x(i-1),y(i-1),z(i-1),t(i-1),sigma,r,b,dx,dy,dz)
          x1 = x(i-1)+0.5*dt*dx
          y1 = y(i-1)+0.5*dt*dy
          z1 = z(i-1)+0.5*dt*dz
          t1 = t(i-1)+0.5*dt
          call dv(x1,y1,z1,t1,sigma,r,b,dx,dy,dz)
          x(i)=x(i-1)+dt*dx
          y(i)=y(i-1)+dt*dy
          z(i)=z(i-1)+dt*dz
10       continue
      else
         do 20 i = 2,nstep
          t(i) = t(i-1)+dt
          call dv(x(i-1),y(i-1),z(i-1),t(i-1),sigma,r,b,dx,dy,dz)
          x(i) = x(i-1)+dt*dx
          y(i) = y(i-1)+dt*dy
          z(i) = z(i-1)+dt*dz
20       continue
      endif
      return
      end
c
      subroutine dv(x0,y0,z0,t0,sigma,r,b,dx,dy,dz)
      implicit real*8 (a-h,o-z)
      dx=sigma*(y0-x0)
      dy=-x0*z0+r*x0-y0
      dz=x0*y0-b*z0
      return
      end
c
      subroutine display(x,y,z,t,sigma,r,b,dt,lsym,nsym,k,n,m)
c
c       Modified to write simple text output to "graph.out" for comparison.
c
      implicit real*8 (a-h,o-z)
      dimension x(1),y(1),z(1),t(1)
      
      open(unit=19, file='graph.out', status='unknown')
      write(19, *) 'Time(s)             x             y             z'
      do 10 i = 1, n
        write(19, *) t(i), x(i), y(i), z(i)
10    continue
      close(19)
      
      print *, 'Data successfully written to graph.out for comparison.'
      
      return
      end