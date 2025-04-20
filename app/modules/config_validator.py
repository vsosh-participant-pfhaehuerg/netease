import re
import nginx

class ConfigValidator:
    def __init__(self):
        self.security_checks = [
            self.check_server_tokens,
            self.check_x_frame_options,
            self.check_content_security_policy,
            self.check_ssl_protocols,
            self.check_ssl_ciphers,
            self.check_add_header_security,
            self.check_large_client_header_buffers,
            self.check_client_max_body_size,
            self.check_limit_req_zone,
            self.check_broad_access_log_format
        ]
    
    def validate_config(self, config_content):
        """Run all security checks on a configuration"""
        issues = []
        
        for check in self.security_checks:
            result = check(config_content)
            if result:
                issues.append(result)
        
        return issues
    
    def check_server_tokens(self, config_content):
        """Check if server_tokens is disabled"""
        if "server_tokens off;" not in config_content:
            return {
                "level": "medium",
                "message": "Server tokens should be disabled",
                "recommendation": "Add 'server_tokens off;' to hide nginx version information",
                "code": "server_tokens off;"
            }
        return None
    
    def check_x_frame_options(self, config_content):
        """Check for X-Frame-Options header"""
        if "X-Frame-Options" not in config_content:
            return {
                "level": "medium",
                "message": "X-Frame-Options header is missing",
                "recommendation": "Add 'add_header X-Frame-Options \"SAMEORIGIN\";' to prevent clickjacking attacks",
                "code": "add_header X-Frame-Options \"SAMEORIGIN\";"
            }
        return None
    
    def check_content_security_policy(self, config_content):
        """Check for Content-Security-Policy header"""
        if "Content-Security-Policy" not in config_content:
            return {
                "level": "medium",
                "message": "Content-Security-Policy header is missing",
                "recommendation": "Add 'add_header Content-Security-Policy \"default-src 'self';\";' to prevent XSS attacks",
                "code": "add_header Content-Security-Policy \"default-src 'self';\";"
            }
        return None
    
    def check_ssl_protocols(self, config_content):
        """Check for secure SSL protocols"""
        if "ssl_protocols" in config_content:
            if "SSLv3" in config_content or "TLSv1 " in config_content:
                return {
                    "level": "high",
                    "message": "Insecure SSL protocols found",
                    "recommendation": "Use secure SSL protocols",
                    "code": "ssl_protocols TLSv1.2 TLSv1.3;"
                }
        elif "ssl" in config_content or "listen 443" in config_content:
            return {
                "level": "medium",
                "message": "SSL protocols not specified",
                "recommendation": "Specify secure SSL protocols",
                "code": "ssl_protocols TLSv1.2 TLSv1.3;"
            }
        return None
    
    def check_ssl_ciphers(self, config_content):
        """Check for secure SSL ciphers"""
        if "ssl_ciphers" not in config_content and ("ssl" in config_content or "listen 443" in config_content):
            return {
                "level": "medium",
                "message": "SSL ciphers not specified",
                "recommendation": "Specify secure SSL ciphers",
                "code": "ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';"
            }
        return None
    
    def check_add_header_security(self, config_content):
        """Check for additional security headers"""
        missing_headers = []
        
        headers = {
            "X-Content-Type-Options": "add_header X-Content-Type-Options \"nosniff\";",
            "X-XSS-Protection": "add_header X-XSS-Protection \"1; mode=block\";",
            "Strict-Transport-Security": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
        }
        
        for header, code in headers.items():
            if header not in config_content:
                missing_headers.append({"header": header, "code": code})
        
        if missing_headers:
            recommendations = "\n".join([h["code"] for h in missing_headers])
            return {
                "level": "medium",
                "message": f"Missing security headers: {', '.join([h['header'] for h in missing_headers])}",
                "recommendation": "Add the following security headers:",
                "code": recommendations
            }
        return None
    
    def check_large_client_header_buffers(self, config_content):
        """Check for large_client_header_buffers directive"""
        if "large_client_header_buffers" not in config_content:
            return {
                "level": "low",
                "message": "large_client_header_buffers not set",
                "recommendation": "Set large_client_header_buffers to limit header size",
                "code": "large_client_header_buffers 4 16k;"
            }
        return None
    
    def check_client_max_body_size(self, config_content):
        """Check if client_max_body_size is set"""
        if "client_max_body_size" not in config_content:
            return {
                "level": "medium",
                "message": "client_max_body_size not set",
                "recommendation": "Set client_max_body_size to limit request body size and prevent DOS attacks",
                "code": "client_max_body_size 10m;"
            }
        return None
    
    def check_limit_req_zone(self, config_content):
        """Check if rate limiting is configured"""
        if "limit_req_zone" not in config_content:
            return {
                "level": "medium",
                "message": "Rate limiting not configured",
                "recommendation": "Configure rate limiting to prevent brute force attacks",
                "code": "limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;"
            }
        return None
        
    def check_broad_access_log_format(self, config_content):
        """Check if access log format is configured properly"""
        if "log_format" not in config_content:
            return {
                "level": "low",
                "message": "Custom log format not defined",
                "recommendation": "Define a custom log format to include useful information",
                "code": "log_format main '$remote_addr - $remote_user [$time_local] \"$request\" $status $body_bytes_sent \"$http_referer\" \"$http_user_agent\" \"$http_x_forwarded_for\"';"
            }
        return None 