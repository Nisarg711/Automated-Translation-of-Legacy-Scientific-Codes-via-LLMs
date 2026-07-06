!
! Motion of Hyperion (modeled as a dumbbell)
! theta = dumbbell angle
! omega = dumbbell angular velocity
! t     = time
!
! RK2 (midpoint method) integration
! Outputs: t, theta, omega to stdout
! Proprietary graphics and file I/O removed — stdout only
!
program hyperion
    implicit none

    integer, parameter :: MAXN = 100000
    real(8), dimension(MAXN) :: theta, omega, t
    real(8) :: xc, vxc, yc, vyc, dt, mr, tot
    integer :: n

    call initialize(xc, vxc, yc, vyc, theta, omega, t, dt, mr, tot)
    call calculate(xc, vxc, yc, vyc, theta, omega, t, dt, mr, tot, n)

end program hyperion


! ---------------------------------------------------------------
! Initialize all variables from stdin
! ---------------------------------------------------------------
subroutine initialize(xc, vxc, yc, vyc, theta, omega, t, dt, mr, tot)
    implicit none
    real(8), intent(out) :: xc, vxc, yc, vyc, dt, mr, tot
    real(8), dimension(*), intent(out) :: theta, omega, t

    read(*,*) mr
    read(*,*) xc
    read(*,*) yc
    read(*,*) vxc
    read(*,*) vyc
    read(*,*) theta(1)
    read(*,*) omega(1)
    read(*,*) dt
    read(*,*) tot

    t(1) = 0.0d0

end subroutine initialize


! ---------------------------------------------------------------
! RK2 integration — prints t, theta, omega at each step
! ---------------------------------------------------------------
subroutine calculate(xc, vxc, yc, vyc, theta, omega, t, dt, mr, tot, n)
    implicit none
    real(8), intent(inout) :: xc, vxc, yc, vyc
    real(8), dimension(*), intent(inout) :: theta, omega, t
    real(8), intent(in) :: dt, mr, tot
    integer, intent(out) :: n

    real(8) :: dvxc, dvyc, domega
    real(8) :: omega1, theta1, t1
    real(8) :: xc1, vxc1, yc1, vyc1
    real(8) :: dvxc2, dvyc2, domega2
    real(8), parameter :: pi = 3.14159265358979323846d0
    integer :: i

    write(*,'(3f20.10)') t(1), theta(1), omega(1)

    i = 0
    do
        i = i + 1
        t(i+1) = t(i) + dt

        ! midpoint estimates (half step)
        call dv(xc, vxc, yc, vyc, omega(i), theta(i), t(i), &
                dvxc, dvyc, domega, mr)

        omega1 = omega(i) + 0.5d0*dt*domega
        theta1 = theta(i) + 0.5d0*dt*omega(i)
        t1     = t(i)     + 0.5d0*dt
        xc1    = xc       + 0.5d0*dt*vxc
        vxc1   = vxc      + 0.5d0*dt*dvxc
        yc1    = yc       + 0.5d0*dt*vyc
        vyc1   = vyc      + 0.5d0*dt*dvyc

        ! full step using midpoint derivatives
        call dv(xc1, vxc1, yc1, vyc1, omega1, theta1, t1, &
                dvxc2, dvyc2, domega2, mr)

        omega(i+1) = omega(i) + dt*domega2
        theta(i+1) = theta(i) + dt*omega1

        ! wrap theta into [-pi, pi]
        if (theta(i+1) >  pi) theta(i+1) = theta(i+1) - 2.0d0*pi
        if (theta(i+1) < -pi) theta(i+1) = theta(i+1) + 2.0d0*pi

        xc  = xc  + dt*vxc1
        vxc = vxc + dt*dvxc2
        yc  = yc  + dt*vyc1
        vyc = vyc + dt*dvyc2

        write(*,'(3f20.10)') t(i+1), theta(i+1), omega(i+1)

        if (t(i+1) >= tot .or. i+1 >= 100000) exit
    end do

    n = i + 1

end subroutine calculate


! ---------------------------------------------------------------
! Compute derivatives for RK2 step
! dvxc, dvyc  = acceleration of centre of mass
! domega      = angular acceleration of dumbbell
! ---------------------------------------------------------------
subroutine dv(xc0, vxc0, yc0, vyc0, omega0, theta0, t0, &
              dvxc, dvyc, domega, mr)
    implicit none
    real(8), intent(in)  :: xc0, vxc0, yc0, vyc0
    real(8), intent(in)  :: omega0, theta0, t0, mr
    real(8), intent(out) :: dvxc, dvyc, domega

    real(8) :: r
    real(8), parameter :: pi = 3.14159265358979323846d0

    r = sqrt(xc0**2 + yc0**2)

    dvxc   = -(4.0d0*pi**2 * mr * xc0) / r**3
    dvyc   = -(4.0d0*pi**2 * mr * yc0) / r**3
    domega = -(12.0d0*pi**2 * mr) &
             * (xc0*sin(theta0) - yc0*cos(theta0)) &
             * (xc0*cos(theta0) + yc0*sin(theta0)) &
             / r**5

end subroutine dv