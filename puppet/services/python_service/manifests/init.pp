class python_service {

  $packages = [
    'python',
    'python-dev',
    'python3',
    'python3-dev',
    'python-virtualenv',
  ]

  package { $packages:
    ensure => present,
  }

}
