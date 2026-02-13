import React from 'react';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full bg-gradient-to-r from-blue-700 via-blue-800 to-indigo-900 text-white py-5 mt-auto shadow-2xl">
      <div className="w-full px-6">
        {/* Footer Content in Compact Grid */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-3 text-sm text-blue-100">
          {/* Physical Address */}
          <div>
            <p className="font-semibold text-white mb-2 text-base">Address</p>
            <p className="leading-tight">Commercial Street, Industrial Area, P.O. Box 74494 - 00200, Nairobi, Kenya.</p>
          </div>

          {/* Email Contacts */}
          <div>
            <p className="font-semibold text-white mb-2 text-base">Email</p>
            <p className="break-all">directorgeneral@nita.go.ke</p>
            <p className="break-all text-blue-100">studentsupport@nita.go.ke</p>
          </div>

          {/* Phone Contacts */}
          <div>
            <p className="font-semibold text-white mb-2 text-base">Phone</p>
            <p>+254-20-2695586/9</p>
            <p>+254-720-917897</p>
          </div>

          {/* Mobile & Hotline */}
          <div>
            <p className="font-semibold text-white mb-2 text-base">Mobile/Hotline</p>
            <p>+254-736-290676</p>
            <p>+254-772-212488</p>
            <p>+254-753-244676</p>
          </div>

          {/* Website & Social */}
          <div>
            <p className="font-semibold text-white mb-2 text-base">Online</p>
            <p><a href="https://nita.go.ke" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">nita.go.ke</a></p>
            <p><a href="https://facebook.com/nita.go.ke" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">@nita.go.ke</a></p>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-blue-500 pt-2">
          <p className="text-center text-sm text-blue-100">
            &copy; {currentYear} National Industrial Training Authority. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
