c
c 2D Random Walk
c Translated from True BASIC to standard Fortran 77
c Output directed to standard output
c
      program walk2d
      dimension x2ave(1000)
      integer nwalks, nsteps
c
      call init(x2ave, nwalks, nsteps)
      call calc(x2ave, nwalks, nsteps)
      call out(x2ave, nsteps)
      stop
      end
c
      subroutine init(x2ave, nwalks, nsteps)
      dimension x2ave(1000)
      integer nwalks, nsteps, i
c
      print *, 'number of steps per walk (max 1000)?'
      read(5, *) nsteps
      print *, 'number of walks?'
      read(5, *) nwalks
c
c     Initialize array
      do 10 i = 1, nsteps
        x2ave(i) = 0.0
 10   continue
      return
      end
c
      subroutine calc(x2ave, nwalks, nsteps)
      dimension x2ave(*)
      integer nwalks, nsteps, i, j
      real x, y, r
c
      do 20 i = 1, nwalks
        x = 0.0
        y = 0.0
        do 10 j = 1, nsteps
c         Using common rand(0) for random number generation
          r = rand(0)
          if(r.le.0.25) then
            x = x + 1.0
          elseif(r.le.0.5) then
            x = x - 1.0
          elseif(r.le.0.75) then
            y = y + 1.0
          else
            y = y - 1.0
          endif
          x2ave(j) = x2ave(j) + x*x + y*y
 10     continue
 20   continue
c
c     Normalize and compute natural log
      do 30 j = 1, nsteps
        x2ave(j) = log(x2ave(j) / real(nwalks))
 30   continue
      return
      end
c
      subroutine out(x2ave, nsteps)
      dimension x2ave(*)
      integer nsteps, i
      real t
c
c     Write directly to standard output instead of graph.out
      print *, 'ln(N)           ln(<R^2>)'
      do 10 i = 1, nsteps
        t = log(real(i))
        print *, t, x2ave(i)
 10   continue
      return
      end