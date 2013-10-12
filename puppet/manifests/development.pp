node 'dev-alpaca-django' {

  stage { 'first':
    before => Stage['main'],
  }

  class { 'apt':
    always_apt_update => true,
    stage             => 'first',
  }

  include utilities_service
  include python_service
  include application_service
  include nginx_service

}
