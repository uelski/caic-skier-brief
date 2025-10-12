import {Text} from "@mantine/core";

export function NavLink({ label, href, icon }: { label?: string, href: string, icon?: string }) {
    return (
        <a style={{ color: "white", textDecoration: "none" }} target="_blank" href={href}>
            {icon && <img src={icon} alt={href} width={24} height={24} />}
            {label && <Text>{label}</Text>}    
        </a>
    )
}